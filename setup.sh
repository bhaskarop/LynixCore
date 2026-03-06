#!/bin/bash
set -euo pipefail

# ─── Config ───────────────────────────────────────────────────────────
APP_NAME="lynixcore-telegram"
APP_DIR="/opt/$APP_NAME"
APP_USER="lynixbot"
PYTHON_VERSION="python3"
SERVICE_FILE="/etc/systemd/system/$APP_NAME.service"
REPO_URL="https://github.com/bhaskarop/LynixCore.git"
REPO_BRANCH="main"

# ─── Colors ───────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ─── Root check ───────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "Please run as root:  sudo bash setup.sh [command]"
fi

# ─── Usage ────────────────────────────────────────────────────────────
show_help() {
    echo ""
    echo -e "  ${CYAN}LynixCore Telegram Bot — Setup Script${NC}"
    echo ""
    echo -e "  ${YELLOW}Usage:${NC}  sudo bash setup.sh [command]"
    echo ""
    echo -e "  ${YELLOW}Commands:${NC}"
    echo "    install   Full first-time setup (default)"
    echo "    update    Git pull + install deps + restart bot"
    echo "    restart   Just restart the bot service"
    echo "    stop      Stop the bot service"
    echo "    logs      Show live bot logs"
    echo "    status    Show bot service status"
    echo "    help      Show this help"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════
#  UPDATE — git pull, install requirements, restart
# ═══════════════════════════════════════════════════════════════════════
do_update() {
    info "Stopping bot..."
    systemctl stop "$APP_NAME" 2>/dev/null || true

    info "Pulling latest code..."
    cd "$APP_DIR"
    git pull origin "$REPO_BRANCH" || warn "Pull skipped (already up to date or no changes)"

    info "Installing Python dependencies..."
    "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt" -q

    info "Starting bot..."
    systemctl start "$APP_NAME"

    echo ""
    info "Update complete! Bot restarted."
    systemctl status "$APP_NAME" --no-pager -l
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════
#  FULL INSTALL
# ═══════════════════════════════════════════════════════════════════════
do_install() {
    # ─── 1. System update & packages ─────────────────────────────────
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

    # ─── 2. Install MongoDB ──────────────────────────────────────────
    if ! command -v mongod &> /dev/null; then
        info "Installing MongoDB 8.0..."

        rm -f /etc/apt/sources.list.d/mongodb-org-*.list

        curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
            gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg

        echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] \
https://repo.mongodb.org/apt/ubuntu noble/mongodb-org/8.0 multiverse" | \
            tee /etc/apt/sources.list.d/mongodb-org-8.0.list

        apt update
        apt install -y mongodb-org
        systemctl enable --now mongod
        info "MongoDB installed and running."
    else
        info "MongoDB already installed, skipping."
    fi

    # ─── 3. Create app user ──────────────────────────────────────────
    if ! id "$APP_USER" &> /dev/null; then
        info "Creating system user: $APP_USER"
        useradd --system --shell /usr/sbin/nologin --home-dir "$APP_DIR" "$APP_USER"
    else
        info "User $APP_USER already exists, skipping."
    fi

    # ─── 4. Deploy application ───────────────────────────────────────
    info "Setting up application directory at $APP_DIR..."

    if [ -n "$REPO_URL" ]; then
        if [ -d "$APP_DIR/.git" ]; then
            info "Git repo exists, pulling latest..."
            cd "$APP_DIR" && git fetch origin && git reset --hard "origin/$REPO_BRANCH"
        else
            info "Cloning repo from $REPO_URL ..."
            rm -rf "$APP_DIR"
            git clone -b "$REPO_BRANCH" "$REPO_URL" "$APP_DIR"
        fi
    else
        mkdir -p "$APP_DIR"
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        if [ "$SCRIPT_DIR" != "$APP_DIR" ]; then
            cp -r "$SCRIPT_DIR"/* "$APP_DIR"/
            cp -r "$SCRIPT_DIR"/.git "$APP_DIR"/ 2>/dev/null || true
            cp -r "$SCRIPT_DIR"/.gitattributes "$APP_DIR"/ 2>/dev/null || true
        fi
    fi

    # ─── 5. Python virtual environment ───────────────────────────────
    info "Creating Python virtual environment..."
    $PYTHON_VERSION -m venv "$APP_DIR/venv"

    info "Installing Python dependencies..."
    "$APP_DIR/venv/bin/pip" install --upgrade pip
    "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

    # ─── 6. Fix ownership ────────────────────────────────────────────
    chown -R "$APP_USER":"$APP_USER" "$APP_DIR"

    # ─── 7. Create systemd service ───────────────────────────────────
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

NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    # ─── 8. Enable & start service ───────────────────────────────────
    info "Reloading systemd and enabling service..."
    systemctl daemon-reload
    systemctl enable "$APP_NAME"
    systemctl start "$APP_NAME"

    # ─── 9. Status ───────────────────────────────────────────────────
    echo ""
    info "Setup complete!"
    echo ""
    echo -e "  ${GREEN}Service status:${NC}"
    systemctl status "$APP_NAME" --no-pager -l
    echo ""
    echo -e "  ${YELLOW}Useful commands:${NC}"
    echo "    sudo bash setup.sh update     # Pull + deps + restart"
    echo "    sudo bash setup.sh restart    # Restart bot"
    echo "    sudo bash setup.sh stop       # Stop bot"
    echo "    sudo bash setup.sh logs       # Live logs"
    echo "    sudo bash setup.sh status     # Check status"
    echo ""
}

# ═══════════════════════════════════════════════════════════════════════
#  COMMAND ROUTER
# ═══════════════════════════════════════════════════════════════════════
CMD="${1:-install}"

case "$CMD" in
    install)  do_install ;;
    update)   do_update ;;
    restart)  info "Restarting bot..."; systemctl restart "$APP_NAME"; systemctl status "$APP_NAME" --no-pager -l ;;
    stop)     info "Stopping bot..."; systemctl stop "$APP_NAME"; info "Bot stopped." ;;
    logs)     journalctl -u "$APP_NAME" -f ;;
    status)   systemctl status "$APP_NAME" --no-pager -l ;;
    help|-h)  show_help ;;
    *)        error "Unknown command: $CMD\n  Run 'sudo bash setup.sh help' for usage." ;;
esac
