#!/bin/bash
set -euo pipefail

# ─── Config ───────────────────────────────────────────────────────────
APP_NAME="lynixcore-telegram"
APP_DIR="/opt/$APP_NAME"
APP_USER="lynixbot"
PYTHON_VERSION="python3"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"

# ─── Colors ───────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ─── Root check ───────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "Please run as root:  sudo bash setup.sh"
fi

# ─── 1. System update & packages ─────────────────────────────────────
info "Updating system packages..."
apt update && apt upgrade -y

info "Installing required system packages..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    gnupg

# ─── 2. Install MongoDB ──────────────────────────────────────────────
if ! command -v mongod &> /dev/null; then
    info "Installing MongoDB..."
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
        gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg

    echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] \
https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | \
        tee /etc/apt/sources.list.d/mongodb-org-7.0.list

    apt update
    apt install -y mongodb-org
    systemctl enable --now mongod
    info "MongoDB installed and running."
else
    info "MongoDB already installed, skipping."
fi

# ─── 3. Create app user ──────────────────────────────────────────────
if ! id "$APP_USER" &> /dev/null; then
    info "Creating system user: $APP_USER"
    useradd --system --shell /usr/sbin/nologin --home-dir "$APP_DIR" "$APP_USER"
else
    info "User $APP_USER already exists, skipping."
fi

# ─── 4. Deploy application ───────────────────────────────────────────
info "Setting up application directory at $APP_DIR..."
mkdir -p "$APP_DIR"

# Copy project files (run this script from the project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ "$SCRIPT_DIR" != "$APP_DIR" ]; then
    cp -r "$SCRIPT_DIR"/* "$APP_DIR"/
    cp -r "$SCRIPT_DIR"/.gitattributes "$APP_DIR"/ 2>/dev/null || true
fi

# ─── 5. Python virtual environment ───────────────────────────────────
info "Creating Python virtual environment..."
$PYTHON_VERSION -m venv "$APP_DIR/venv"

info "Installing Python dependencies..."
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# ─── 6. Fix ownership ────────────────────────────────────────────────
chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

# ─── 7. Create systemd service ───────────────────────────────────────
info "Creating systemd service: $APP_NAME"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=LynixCore Telegram Bot
After=network.target mongod.service
Wants=mongod.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/python main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Hardening
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# ─── 8. Enable & start service ───────────────────────────────────────
info "Reloading systemd and enabling service..."
systemctl daemon-reload
systemctl enable "$APP_NAME"
systemctl start "$APP_NAME"

# ─── 9. Status ────────────────────────────────────────────────────────
echo ""
info "Setup complete!"
echo ""
echo -e "  ${GREEN}Service status:${NC}"
systemctl status "$APP_NAME" --no-pager -l
echo ""
echo -e "  ${YELLOW}Useful commands:${NC}"
echo "    sudo systemctl status  $APP_NAME    # Check status"
echo "    sudo systemctl restart $APP_NAME    # Restart bot"
echo "    sudo systemctl stop    $APP_NAME    # Stop bot"
echo "    sudo journalctl -u $APP_NAME -f     # Live logs"
echo ""
