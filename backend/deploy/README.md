# Deploying the backend on an Oracle Cloud Always Free VM

An always-on VM at ₹0. This folder is the whole deployment: one setup script, and the unit files
it installs.

Written for Oracle's Always Free VM, but it works on **any** Ubuntu 22.04/24.04 machine with a
public IP — including Google Cloud's always-free `e2-micro`. Only the VM's IP address changes;
the script, the DNS record and the commands are identical.

> **Never done this before?** Read [`../../docs/FIRST_DEPLOY.md`](../../docs/FIRST_DEPLOY.md)
> first — the same steps in plain English, no computer-science background assumed.

```
deploy/
  setup.sh              one-shot provisioning (run once, as root)
  elibrary.service      systemd unit → /etc/systemd/system/
  nginx.conf            reverse proxy → /etc/nginx/sites-available/elibrary
  backup.sh             nightly DB + uploads backup → /usr/local/bin/elibrary-backup
  deploy.sh             redeploy after a push
```

## 1. Create the VM

1. Sign up for Oracle Cloud Free Tier. Everything below is an **Always Free** resource.
2. **Compute → Instances → Create instance.**
   - **Image:** Ubuntu 22.04 or 24.04
   - **Shape:** `VM.Standard.A1.Flex` (Ampere/ARM, up to 4 OCPU / 24 GB free) or
     `VM.Standard.E2.1.Micro` (AMD, always free)
   - **SSH keys:** upload your public key
   - Note the **public IP** when it's running.

## 2. Open the ports — two places, both required

Oracle blocks everything but SSH by default, and its Ubuntu images add their own firewall rules.
**Missing either step is the most common reason the site can't reach the API.**

- **Cloud side:** Networking → VCN → Security Lists → *Default* → **Add Ingress Rules** for
  `0.0.0.0/0` on TCP **80** and **443**.
- **Machine side:** `setup.sh` adds the `iptables` rules for you. If you set up by hand:
  ```bash
  iptables -I INPUT -p tcp --dport 80  -j ACCEPT
  iptables -I INPUT -p tcp --dport 443 -j ACCEPT
  netfilter-persistent save
  ```

## 3. Run the setup

```bash
ssh ubuntu@<public-ip>
git clone --depth 1 https://github.com/kartik-h6/e-library.git ~/e-library
sudo DOMAIN=<your-hostname> bash ~/e-library/backend/deploy/setup.sh
```

Then edit the environment file and restart:

```bash
sudo nano /etc/elibrary/elibrary.env     # set DEPT_MASTER_PASSWORD and DRIVE_FOLDER_URL
sudo systemctl restart elibrary
```

Check it:

```bash
systemctl status elibrary
curl -s localhost:8000/api/public/library | head -c 200
```

## 4. HTTPS — and why you need a hostname

The public site is served over HTTPS, and a browser will **block** an HTTPS page from calling an
HTTP API. So the backend must be HTTPS too, which means it needs a hostname — not a bare IP.

- **This project:** `elibrary.techstudyhubcore.in` — an `A` record in Cloudflare pointing at the VM,
  passed as `DOMAIN`; `setup.sh` runs certbot for you.
- **No domain yet?** A free DuckDNS subdomain works the same way, with the same certbot step.

If you'd rather not open ports at all, a **Cloudflare Tunnel** gives you HTTPS with no inbound
ports and no certificate management — it does add a Cloudflare dependency, so it's a trade, not a
free lunch.

## 5. Point the site at it

```bash
cd frontend
API_BASE=https://<host> SIGN_IN_URL=https://<host>/login python3 build/generate.py
git add -A && git commit -m "Connect site to the staff service" && git push
```

## 6. Day two

| Task | Command |
|---|---|
| Deploy a new version | `sudo bash /opt/elibrary/backend/deploy/deploy.sh` |
| View logs | `journalctl -u elibrary -n 100 -f` |
| Backups | automatic nightly to `/var/backups/elibrary` (14 days) |
| Restore | stop the service, copy a `elib-*.db` back to `/var/lib/elibrary/elib.db`, start it |
| Change a setting | edit `/etc/elibrary/elibrary.env`, then `systemctl restart elibrary` |

## Notes

- **The database is one SQLite file** at `/var/lib/elibrary/elib.db`. That's deliberate at this
  scale — back it up by copying it, move it anywhere, open it with any SQLite tool.
- **The service binds to `127.0.0.1` only.** nginx is the only thing exposed to the internet.
- **Nothing secret is in the repository.** All configuration is in `/etc/elibrary/elibrary.env`,
  readable only by root.
- **Students never touch this VM.** If it's down, the public site still works; only the staff
  dashboard and live material are affected.
