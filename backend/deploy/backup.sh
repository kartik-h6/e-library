#!/usr/bin/env bash
# Nightly backup of the database and uploads. Installed to /usr/local/bin/elibrary-backup
# and run by /etc/cron.d/elibrary-backup. Keeps 14 days.
set -euo pipefail

DB=/var/lib/elibrary/elib.db
UPLOADS=/opt/elibrary/backend/uploads
DEST=/var/backups/elibrary
STAMP="$(date +%Y%m%d-%H%M)"

mkdir -p "$DEST"

# sqlite3 .backup is safe on a live database; a plain cp is not.
if [ -f "$DB" ]; then
  sqlite3 "$DB" ".backup '$DEST/elib-$STAMP.db'"
fi

if [ -d "$UPLOADS" ]; then
  tar -czf "$DEST/uploads-$STAMP.tgz" -C "$(dirname "$UPLOADS")" "$(basename "$UPLOADS")"
fi

find "$DEST" -type f -mtime +14 -delete

echo "backup complete: $DEST ($(du -sh "$DEST" | cut -f1))"
