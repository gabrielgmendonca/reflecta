#!/bin/bash
set -e

# =============================================================================
# Reflecta Docker Deployment Script
# =============================================================================
# Usage: ./deploy.sh <server-ip> [options]
#
# Options:
#   --setup    Install Docker on server (first time only)
#   --deploy   Build and deploy the application (default)
#   --restart  Restart containers only
#   --logs     View application logs
#   --stop     Stop the application
# =============================================================================

# Configuration
SSH_USER="mendonca"
APP_NAME="reflecta"
APP_DIR="/home/${SSH_USER}/${APP_NAME}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: ./deploy.sh <server-ip> [--setup|--deploy|--restart|--logs|--stop]"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh 192.168.1.100 --setup   # Install Docker (first time)"
    echo "  ./deploy.sh 192.168.1.100           # Deploy application"
    echo "  ./deploy.sh 192.168.1.100 --logs    # View logs"
    echo "  ./deploy.sh 192.168.1.100 --stop    # Stop application"
    exit 1
fi

SERVER_IP="$1"
ACTION="${2:---deploy}"
SSH_CMD="ssh ${SSH_USER}@${SERVER_IP}"

log "Target server: ${SSH_USER}@${SERVER_IP}"
log "Action: ${ACTION}"

# =============================================================================
# Install Docker (run once)
# =============================================================================
setup_server() {
    log "Installing Docker on server..."

    $SSH_CMD << 'SETUP_EOF'
set -e

# Check if Docker is already installed
if command -v docker &> /dev/null; then
    echo "Docker is already installed"
    docker --version
else
    echo ">>> Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo ">>> Docker installed! Please log out and back in, then run deploy again."
fi

# Install docker-compose plugin if not present
if ! docker compose version &> /dev/null; then
    echo ">>> Installing Docker Compose plugin..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
fi

echo ">>> Creating app directory..."
mkdir -p ~/reflecta

echo ">>> Setup complete!"
SETUP_EOF

    log "Docker setup complete."
    log "IMPORTANT: Log out and back into the server, then run: ./deploy.sh ${SERVER_IP}"
}

# =============================================================================
# Deploy Application
# =============================================================================
deploy_app() {
    log "Deploying application with Docker..."

    # Check if .env.production exists locally
    if [ ! -f "$(dirname "$0")/.env.production" ]; then
        warn ".env.production not found locally. Creating from example..."
        cp "$(dirname "$0")/.env.production.example" "$(dirname "$0")/.env.production"
        # Generate a random secret key
        SECRET_KEY=$(openssl rand -hex 32)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/change-this-to-a-long-random-string/${SECRET_KEY}/" "$(dirname "$0")/.env.production"
        else
            sed -i "s/change-this-to-a-long-random-string/${SECRET_KEY}/" "$(dirname "$0")/.env.production"
        fi
        log "Generated .env.production with random SECRET_KEY"
    fi

    # Sync files to server
    log "Syncing files to server..."
    rsync -avz --progress \
        --exclude 'node_modules' \
        --exclude 'venv' \
        --exclude '__pycache__' \
        --exclude '.git' \
        --exclude '*.pyc' \
        --exclude 'retro.db' \
        --exclude 'reflecta.db' \
        --exclude 'dist' \
        --exclude '.pytest_cache' \
        --exclude '.env' \
        "$(dirname "$0")/" \
        "${SSH_USER}@${SERVER_IP}:${APP_DIR}/"

    # Build and start on server
    log "Building and starting containers..."
    $SSH_CMD << 'DEPLOY_EOF'
set -e
cd ~/reflecta

echo ">>> Building Docker image..."
docker compose build

echo ">>> Starting application..."
docker compose up -d

echo ">>> Waiting for startup..."
sleep 3

echo ">>> Container status:"
docker compose ps

echo ""
echo ">>> Deployment complete!"
DEPLOY_EOF

    log "Deployment complete!"
    log "Access your app at: http://${SERVER_IP}"
}

# =============================================================================
# Restart Containers
# =============================================================================
restart_app() {
    log "Restarting containers..."

    $SSH_CMD << 'RESTART_EOF'
set -e
cd ~/reflecta
docker compose restart
docker compose ps
RESTART_EOF

    log "Containers restarted!"
}

# =============================================================================
# View Logs
# =============================================================================
view_logs() {
    log "Showing logs (Ctrl+C to exit)..."
    $SSH_CMD "cd ~/reflecta && docker compose logs -f"
}

# =============================================================================
# Stop Application
# =============================================================================
stop_app() {
    log "Stopping application..."

    $SSH_CMD << 'STOP_EOF'
set -e
cd ~/reflecta
docker compose down
echo ">>> Application stopped"
STOP_EOF

    log "Application stopped!"
}

# =============================================================================
# Main
# =============================================================================
case "$ACTION" in
    --setup)
        setup_server
        ;;
    --deploy)
        deploy_app
        ;;
    --restart)
        restart_app
        ;;
    --logs)
        view_logs
        ;;
    --stop)
        stop_app
        ;;
    *)
        error "Unknown action: $ACTION"
        ;;
esac
