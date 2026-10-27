# Your first deployment — in plain English

No computer-science background needed. This is a recipe: follow it top to bottom.

> **This project's setup:** domain registered at **BigRock**, DNS managed on **Cloudflare**, public
> site on **GitHub Pages**, staff service on an **Oracle Always Free VM** at
> `library.techstudyhubcore.in`.

---

## 1. The words, explained

| Word | What it actually means |
|---|---|
| **Server / VM** | A computer you rent that never switches off, sitting in a data centre. You type commands to it over the internet instead of sitting in front of it. |
| **SSH** | The secure text line into that computer. You open a terminal and type. |
| **IP address** | Its phone number — something like `129.154.60.12`. |
| **Domain / subdomain** | A readable name that points at that number, so people type `library.yoursite.org` instead of the number. |
| **Port** | A numbered door on the computer. Door **80** is ordinary web, door **443** is secure web. |
| **HTTPS / TLS certificate** | The padlock in the browser. Let's Encrypt issues one free. |
| **Firewall** | The rulebook saying which doors are open. |

**Why the padlock matters here:** our public website is served over HTTPS (padlock). A browser
**refuses** to let an HTTPS page talk to an address without a padlock. So the backend needs one too
— and a padlock can only be issued for a *name*, never for a bare number. That is the only reason
you need a domain or subdomain. Nothing more.

---

## 2. What you need before you start

1. **An Oracle Cloud account** — free. Oracle asks for a card to confirm you are a real person.
   **Always Free resources are not charged**, though a small temporary hold may appear.
2. **A subdomain** — you already own `techstudyhubcore.in`; in Step 0 you point `elibrary.` at the
   machine. Nothing to buy.
3. **A private key file** — Oracle gives you one when you create the machine. It is your login. Keep
   it safe; you cannot recover it.
4. **Two decisions**, nothing technical:
   - the password every department head will use to sign in;
   - the link to your shared Google Drive folder.

---

## 3. Step by step (about 30 minutes)

### Step 0 — Point the subdomain at the machine (do this first)

`techstudyhubcore.in` is registered at **BigRock**, but its DNS is managed on **Cloudflare** — so the
record goes in Cloudflare, not BigRock.

1. Sign in at **dash.cloudflare.com** and click `techstudyhubcore.in`.
2. Left menu → **DNS** → **Records** → **Add record**.
3. Fill it in exactly like this:

   | Field | Value |
   |---|---|
   | Type | `A` |
   | Name | `elibrary` |
   | IPv4 address | your machine's public IP |
   | Proxy status | **DNS only** — the **grey** cloud, *not* the orange one |
   | TTL | Auto |

4. **Save.** You now have `elibrary.techstudyhubcore.in`.

**Two Cloudflare things worth knowing:**

- Keep the cloud **grey** for now. Orange puts Cloudflare in front of your server — genuinely useful
  later, but it adds one setting that breaks everything if it is wrong.
- If you ever switch it to orange, you **must** set **SSL/TLS → Overview → Full (strict)**. Never
  choose "Flexible": with our HTTP→HTTPS redirect it causes an endless redirect loop.

Your main site at `techstudyhubcore.in` is untouched — a subdomain is a separate signboard, not a
new building.

### Step 1 — Create the machine

1. Sign in to **cloud.oracle.com**.
2. **Compute → Instances → Create instance.**
3. Name it `elibrary`. Leave the compartment as it is.
4. Under **Image**, choose **Ubuntu 22.04** (or 24.04).
5. Under **Shape**, pick **`VM.Standard.E2.1.Micro`** — it is Always Free and always available. (The
   more powerful ARM shape is also free but is often out of stock.)
6. Under **Add SSH keys**, choose **Generate a key pair for me**, then **download the private key**.
7. Click **Create**. Wait a minute. Copy the **Public IP address** shown on the instance page.
8. Go back to Cloudflare and paste that IP into the `elibrary` record. Save. Wait 2 minutes.

### Step 2 — Open the two doors

Both are needed. Missing one is the usual reason "it doesn't load".

**Door one, in Oracle's website:**
Networking → Virtual Cloud Networks → your VCN → Security Lists → *Default Security List* →
**Add Ingress Rules**. Add two rules, both with Source `0.0.0.0/0`, Destination Port `80` and `443`.

**Door two, on the machine itself:** the setup script in Step 3 opens these for you automatically.
If you ever do it by hand, it is two `iptables` lines (they are in `backend/deploy/README.md`).

### Step 3 — Log in and run the script

Open a terminal. On Windows use *PowerShell*; on Mac/Linux use *Terminal*.

```bash
# make the key file private (required, once)
chmod 600 /path/to/your-private-key.key

# log in  (type "yes" if it asks about authenticity)
ssh -i /path/to/your-private-key.key ubuntu@YOUR_PUBLIC_IP
```

You are now "inside" the machine. Run these three lines:

```bash
git clone --depth 1 https://github.com/kartik-h6/e-library.git ~/e-library
sudo DOMAIN=elibrary.techstudyhubcore.in bash ~/e-library/backend/deploy/setup.sh
sudo systemctl status elibrary
```

That installs everything, starts the service, sets up the website in front of it, and gets the
padlock. The last line should say **active (running)** in green. Press `q` to exit.

### Step 4 — Set your two settings

```bash
sudo nano /etc/elibrary/elibrary.env
```

Change these two lines, then press `Ctrl+O`, `Enter`, `Ctrl+X` to save and exit:

```
DEPT_MASTER_PASSWORD=paste-a-strong-password-here
DRIVE_FOLDER_URL=paste-your-drive-folder-link-here
```

Then:

```bash
sudo systemctl restart elibrary
```

### Step 5 — Check it works

Open a browser on your own laptop and go to:

```
https://elibrary.techstudyhubcore.in/login
```

You should see the sign-in page **with a padlock**. Sign in as `admin@techstudyhubcore.in` / `admin123`
(change this password soon). If you see the dashboard with 88 subjects, the backend is done.

### Step 6 — Connect the public site to it

On your own laptop, in the project folder:

```bash
cd frontend
API_BASE=https://elibrary.techstudyhubcore.in SIGN_IN_URL=https://elibrary.techstudyhubcore.in/login python3 build/generate.py
git add -A && git commit -m "Connect site to the staff service" && git push
```

Two minutes later the live site's **Staff** link points at your service, and subject pages pull
material live.

---

## 4. What success looks like

- `https://elibrary.techstudyhubcore.in/login` shows the sign-in page with a padlock.
- Signing in as a department head shows only that department's subjects plus Common Courses.
- Publishing something as staff makes it appear on the public site after a refresh.

## 5. About the domain

**Host this on your own domain, not a college's.** A site on a college's address looks officially
endorsed by them, and you have not been given that permission. Every page already says this is an
independent study platform, not affiliated with the PCI or any institution — keep that true.

`elibrary.techstudyhubcore.in` is the staff portal and API. The public library stays on GitHub Pages
for now. If you later want the public site on your own domain too, point a second subdomain (for
example `library.techstudyhubcore.in`) at GitHub Pages, and add that origin to `CORS_ORIGINS` — the
browser will block live material otherwise.

If an institution later wants to host its own copy, that is fine too: this same script runs on any
Ubuntu machine they provide.

## 6. If Oracle turns you down

Oracle sometimes rejects signups or has no free machines in your region. Options, best first:

1. **Google Cloud's always-free VM.** The closest match to Oracle: one `e2-micro` instance with a
   30 GB disk, free with no end date, in `us-west1`, `us-central1` or `us-east1`. Signup asks for a
   card to confirm you are real (a temporary hold of about $1, never an actual charge). The same
   `setup.sh` works unchanged. It is a US region, so expect ~200 ms latency from India — irrelevant
   for a notes library.
2. **A small VPS in India** — around ₹250–400 a month. Always on, persistent, low latency, and no
   signup lottery. The most reliable option, and the same script works on it.
3. **Defer the backend.** The site already works fully static. Add the backend when staff
   self-serve actually matters — there is no content yet, so there is no rush.

**Do not use Render's free tier for this.** Its filesystem is *ephemeral*: a local SQLite database
and uploaded files are **erased** every time the service redeploys, restarts, or spins down after
inactivity. Your material would silently disappear. Persistent disks there require a paid instance,
and free Postgres expires after 30 days.

**Cloudflare cannot host this backend as it stands.** Cloudflare runs JavaScript Workers, not a
long-running Python process with a SQLite file. Moving there would mean rewriting the backend, not
migrating it. (Cloudflare *can* stay in front of it as your DNS and CDN — that part is unchanged.)

## 7. When you get stuck

Run this on the machine and send me the output:

```bash
sudo journalctl -u elibrary -n 50 --no-pager
```

That is the service's log — it says exactly what went wrong. Almost every problem at this stage is
one of: the name not pointing at the right IP, or a door still closed.
