#!/usr/bin/env bash
# Redeploy after a push: pull, install any new dependencies, restart.
#   sudo bash /opt/elibrary/backend/deploy/deploy.sh
set -euo pipefail

APP_DIR=/opt/elibrary
SVC=elibrary

[ "$(id -u)" -eq 0 ] || { echo "Run as root: sudo bash deploy.sh"; exit 1; }

echo "==> pulling"
git -C "$APP_DIR" pull --ff-only

echo "==> dependencies"
sudo -u "$SVC" "$APP_DIR/backend/.venv/bin/pip" install -q -r "$APP_DIR/backend/requirements.txt"

echo "==> restart"
systemctl restart "$SVC"
sleep 2
systemctl --no-pager --lines=5 status "$SVC" || true

echo "==> health"
curl -fsS http://127.0.0.1:8000/api/public/library >/dev/null \
  && echo "    API responding" \
  || { echo "    API NOT responding — check: journalctl -u $SVC -n 50"; exit 1; }
