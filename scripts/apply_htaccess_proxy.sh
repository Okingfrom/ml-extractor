#!/bin/bash
# Backup and insert proxy rules at top of public_html/.htaccess
set -euo pipefail
APP_ROOT="$HOME/repositories/ml-extractor"
DOCROOT="$HOME/public_html"
HTACCESS="$DOCROOT/.htaccess"
BACKUP="$HTACCESS.bak.$(date +%s)"

if [ ! -f "$HTACCESS" ]; then
  echo "No .htaccess found at $HTACCESS"
  exit 1
fi

cp "$HTACCESS" "$BACKUP"

cat > /tmp/proxy_block_$$.tmp <<'PROXY'
RewriteEngine On

# Opcional: forzar HTTPS
RewriteCond %{HTTPS} !=on
RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]

# Proxy inverso hacia tu app FastAPI (Uvicorn)
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ http://127.0.0.1:8000/$1 [P,L]
PROXY

# Prepend proxy block
cat /tmp/proxy_block_$$.tmp "$HTACCESS" > "$HTACCESS.tmp"
mv "$HTACCESS.tmp" "$HTACCESS"
rm -f /tmp/proxy_block_$$.tmp

echo "Inserted proxy block at top of $HTACCESS (backup saved to $BACKUP)"
