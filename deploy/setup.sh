#!/bin/bash
# ================================================
#  ZConnect — One-shot VPS Setup Script
#  Run as root on Ubuntu 24.04
#  Usage: bash setup.sh <your-github-repo-url>
# ================================================

set -e   # stop on any error
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
log() { echo -e "${GREEN}[ZConnect]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

REPO_URL=${1:-"https://github.com/YOUR_USERNAME/ZConnect.git"}
APP_DIR="/var/www/zconnect"

log "Step 1/9 — Updating system packages..."
apt-get update -qq && apt-get upgrade -y -qq

log "Step 2/9 — Installing dependencies..."
apt-get install -y -qq \
    python3 python3-pip python3-venv \
    nginx git curl ufw

log "Step 3/9 — Cloning repository..."
mkdir -p $APP_DIR
if [ -d "$APP_DIR/.git" ]; then
    warn "Repo already exists — pulling latest..."
    cd $APP_DIR && git pull
else
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

log "Step 4/9 — Creating Python virtual environment..."
python3 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate

log "Step 5/9 — Installing Python packages..."
pip install --quiet --upgrade pip
pip install --quiet -r $APP_DIR/requirements.txt

log "Step 6/9 — Creating .env production file..."
if [ ! -f "$APP_DIR/.env" ]; then
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    SERVER_IP=$(curl -s ifconfig.me)
    cat > $APP_DIR/.env << EOF
SECRET_KEY=$SECRET
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,srv1499287.hstgr.cloud
EOF
    log ".env created with auto-generated secret key"
else
    warn ".env already exists — skipping"
fi

log "Step 7/9 — Running migrations & collecting static files..."
source $APP_DIR/venv/bin/activate
cd $APP_DIR
python manage.py migrate --run-syncdb
python manage.py collectstatic --noinput

log "Step 8/9 — Setting up systemd service..."
cp $APP_DIR/deploy/zconnect.service /etc/systemd/system/zconnect.service
systemctl daemon-reload
systemctl enable zconnect
systemctl restart zconnect
sleep 2
systemctl status zconnect --no-pager

log "Step 9/9 — Setting up Nginx..."
cp $APP_DIR/deploy/nginx.conf /etc/nginx/sites-available/zconnect
ln -sf /etc/nginx/sites-available/zconnect /etc/nginx/sites-enabled/zconnect
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

log "Setting up firewall..."
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable

echo ""
echo "================================================"
echo "  ✅  ZConnect is LIVE!"
echo "  🌐  http://$(curl -s ifconfig.me)"
echo "  🔑  Create admin: cd $APP_DIR && source venv/bin/activate && python create_superuser.py"
echo "================================================"
