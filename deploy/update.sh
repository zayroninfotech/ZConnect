#!/bin/bash
# ================================================
#  ZConnect — Pull latest code & restart
#  Run whenever you push new changes to GitHub
#  Usage: bash /var/www/zconnect/deploy/update.sh
# ================================================
set -e
GREEN='\033[0;32m'; NC='\033[0m'
log() { echo -e "${GREEN}[ZConnect]${NC} $1"; }

APP_DIR="/var/www/zconnect"
cd $APP_DIR

log "Pulling latest code from GitHub..."
git pull

log "Installing any new packages..."
source venv/bin/activate
pip install --quiet -r requirements.txt

log "Running migrations..."
python manage.py migrate --run-syncdb

log "Collecting static files..."
python manage.py collectstatic --noinput

log "Restarting ZConnect service..."
systemctl restart zconnect

log "Done! App updated ✅"
systemctl status zconnect --no-pager
