#!/usr/bin/env bash
# Provision a fresh Ubuntu VM (Oracle Cloud Always Free) to run the TechStudyHubCore Pharmacy backend.
#
#   sudo DOMAIN=library.example.com bash setup.sh
#
# DOMAIN is optional. Without it nginx serves plain HTTP on the public IP, which is enough to
# test — but the public site is HTTPS, so browsers will block it until the API is HTTPS too.
# Give it a hostname you own before pointing the site at it.
set -euo pipefail

DOMAIN="${DOMAIN:-}"
REPO="${REPO:-https://github.com/kartik-h6/e-library.git}"
APP_DIR=/opt/elibrary
DATA_DIR=/var/lib/elibrary
CONF_DIR=/etc/elibrary
SVC=elibrary

[ "$(id -u)" -eq 0 ] || { echo "Run as root: sudo DOMAIN=... bash setup.sh"; exit 1; }

echo "==> packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y python3 python3-venv python3-pip nginx git sqlite3 certbot python3-certbot-nginx

echo "==> service user"
id -u "$SVC" >/dev/null 2>&1 || useradd --system --create-home --shell /usr/sbin/nologin "$SVC"

echo "==> code"
mkdir -p "$APP_DIR"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone --depth 1 "$REPO" "$APP_DIR"
fi

echo "==> data + config"
mkdir -p "$DATA_DIR" "$CONF_DIR"
chown -R "$SVC:$SVC" "$DATA_DIR"

echo "==> virtualenv + dependencies"
[ -d "$APP_DIR/backend/.venv" ] || sudo -u "$SVC" python3 -m venv "$APP_DIR/backend/.venv"
sudo -u "$SVC" "$APP_DIR/backend/.venv/bin/pip" install --upgrade pip
sudo -u "$SVC" "$APP_DIR/backend/.venv/bin/pip" install -r "$APP_DIR/backend/requirements.txt"

echo "==> environment file"
if [ ! -f "$CONF_DIR/$SVC.env" ]; then
  SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
  cat > "$CONF_DIR/$SVC.env" <<EOF
DATABASE_URL=sqlite:///$DATA_DIR/elib.db
SESSION_SECRET=$SECRET
COOKIE_SECURE=1
DRIVE_FOLDER_URL=
PUBLIC_SITE_URL=https://pharmacy.techstudyhubcore.in
CORS_ORIGINS=https://pharmacy.techstudyhubcore.in,https://kartik-h6.github.io
EOF
  chmod 600 "$CONF_DIR/$SVC.env"
  echo "    wrote $CONF_DIR/$SVC.env — set DRIVE_FOLDER_URL, then restart"
fi

echo "==> systemd service"
cp "$APP_DIR/backend/deploy/elibrary.service" /etc/systemd/system/$SVC.service
systemctl daemon-reload
systemctl enable "$SVC"
systemctl restart "$SVC"

echo "==> nginx"
sed "s/__DOMAIN__/${DOMAIN:-_}/" "$APP_DIR/backend/deploy/nginx.conf" > /etc/nginx/sites-available/$SVC
ln -sf /etc/nginx/sites-available/$SVC /etc/nginx/sites-enabled/$SVC
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "==> firewall (Oracle images block everything but SSH by default)"
if command -v iptables >/dev/null 2>&1; then
  for port in 80 443; do
    iptables -C INPUT -p tcp --dport "$port" -j ACCEPT 2>/dev/null \
      || iptables -I INPUT -p tcp --dport "$port" -j ACCEPT
  done
  command -v netfilter-persistent >/dev/null 2>&1 && netfilter-persistent save || true
fi

echo "==> nightly backup"
install -m 0755 "$APP_DIR/backend/deploy/backup.sh" /usr/local/bin/elibrary-backup
printf '0 3 * * * root /usr/local/bin/elibrary-backup\n' > /etc/cron.d/elibrary-backup

if [ -n "$DOMAIN" ]; then
  echo "==> TLS for $DOMAIN"
  if ! certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos \
          --register-unsafely-without-email --redirect; then
    echo "!! TLS FAILED for $DOMAIN — DNS may not point at this machine yet." >&2
    echo "   Fix the DNS record, then re-run: certbot --nginx -d $DOMAIN" >&2
    echo "   The service is installed but NOT ready to expose. Stopping." >&2
    exit 1
  fi
fi

echo
echo "Done. Next:"
echo "  0. Create the admin account — nothing is seeded:"
echo "       cd $APP_DIR/backend && sudo -u $SVC .venv/bin/python -m app.manage create-admin --email you@example.com"
echo "  1. Edit $CONF_DIR/$SVC.env (DRIVE_FOLDER_URL), then: systemctl restart $SVC"
echo "  2. Open ports 80 and 443 in the Oracle VCN security list (Networking → VCN → Security Lists)."
echo "  3. Check:  systemctl status $SVC  &&  curl -s localhost:8000/api/public/library"
echo "  4. Point the site at it:"
echo "       API_BASE=https://<host> SIGN_IN_URL=https://<host>/login python3 frontend/build/generate.py"
