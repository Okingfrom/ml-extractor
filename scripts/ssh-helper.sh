#!/bin/bash

# SSH Connection Helper for ML-Extractor Deployment
# This script helps manage SSH connections to your cPanel/hosting server

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (update these values)
SERVER_IP=""
USERNAME=""
SSH_KEY_PATH="$HOME/.ssh/ml-extractor-key"
DEPLOY_DIR="$HOME/app_ml_extractor"
SSH_CONFIG_ALIAS="ml-extractor-prod"

print_help() {
    echo -e "${BLUE}ML-Extractor SSH Connection Helper${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}setup${NC}        Setup SSH configuration"
    echo -e "  ${GREEN}test${NC}         Test SSH connection"
    echo -e "  ${GREEN}connect${NC}      Connect to server"
    echo -e "  ${GREEN}deploy${NC}       Deploy application"
    echo -e "  ${GREEN}status${NC}       Check application status"
    echo -e "  ${GREEN}logs${NC}         View application logs"
    echo -e "  ${GREEN}restart${NC}      Restart application"
    echo -e "  ${GREEN}upload${NC}       Upload local files to server"
    echo -e "  ${GREEN}download${NC}     Download files from server"
    echo -e "  ${GREEN}info${NC}         Show server information"
    echo ""
}

check_config() {
    if [[ -z "$SERVER_IP" || -z "$USERNAME" ]]; then
        echo -e "${RED}Error: Server configuration not set!${NC}"
        echo "Please edit this script and set SERVER_IP and USERNAME variables."
        echo "Example:"
        echo '  SERVER_IP="your-server.com"'
        echo '  USERNAME="your-cpanel-username"'
        exit 1
    fi
}

setup_ssh() {
    echo -e "${BLUE}Setting up SSH configuration...${NC}"
    
    # Check if SSH key exists
    if [[ ! -f "$SSH_KEY_PATH" ]]; then
        echo -e "${YELLOW}SSH key not found. Generating new key...${NC}"
        read -p "Enter your email for SSH key: " email
        ssh-keygen -t ed25519 -C "$email" -f "$SSH_KEY_PATH"
        echo -e "${GREEN}SSH key generated: $SSH_KEY_PATH${NC}"
    fi
    
    # Set proper permissions
    chmod 600 "$SSH_KEY_PATH"
    chmod 644 "$SSH_KEY_PATH.pub"
    
    # Create SSH config entry
    SSH_CONFIG="$HOME/.ssh/config"
    if ! grep -q "$SSH_CONFIG_ALIAS" "$SSH_CONFIG" 2>/dev/null; then
        echo -e "${YELLOW}Adding SSH config entry...${NC}"
        cat >> "$SSH_CONFIG" << EOF

# ML-Extractor Production Server
Host $SSH_CONFIG_ALIAS
    HostName $SERVER_IP
    User $USERNAME
    Port 22
    IdentityFile $SSH_KEY_PATH
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
EOF
        chmod 600 "$SSH_CONFIG"
        echo -e "${GREEN}SSH config entry added${NC}"
    fi
    
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Copy your public key to the server:"
    echo "   ssh-copy-id -i $SSH_KEY_PATH.pub $SSH_CONFIG_ALIAS"
    echo "2. Or manually add this public key to your server:"
    echo -e "${YELLOW}$(cat $SSH_KEY_PATH.pub)${NC}"
}

test_connection() {
    echo -e "${BLUE}Testing SSH connection...${NC}"
    check_config
    
    if ssh -o ConnectTimeout=10 "$SSH_CONFIG_ALIAS" "echo 'Connection successful!'" 2>/dev/null; then
        echo -e "${GREEN}✓ SSH connection successful${NC}"
        return 0
    else
        echo -e "${RED}✗ SSH connection failed${NC}"
        echo "Try: ssh-copy-id -i $SSH_KEY_PATH.pub $SSH_CONFIG_ALIAS"
        return 1
    fi
}

connect_ssh() {
    echo -e "${BLUE}Connecting to server...${NC}"
    check_config
    ssh "$SSH_CONFIG_ALIAS"
}

deploy_app() {
    echo -e "${BLUE}Deploying application...${NC}"
    check_config
    
    if ! test_connection; then
        echo -e "${RED}Cannot deploy: SSH connection failed${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Running deployment script...${NC}"
    ./scripts/deploy_to_server.sh
    echo -e "${GREEN}Deployment completed${NC}"
}

check_status() {
    echo -e "${BLUE}Checking application status...${NC}"
    check_config
    
    ssh "$SSH_CONFIG_ALIAS" << 'EOF'
echo "=== System Information ==="
uname -a
echo ""
echo "=== Disk Usage ==="
df -h ~
echo ""
echo "=== Application Directory ==="
ls -la ~/app_ml_extractor/ 2>/dev/null || echo "App directory not found"
echo ""
echo "=== Python Environment ==="
cd ~/app_ml_extractor 2>/dev/null && source .venv/bin/activate && python --version && pip list | head -10 || echo "Python environment not found"
echo ""
echo "=== Running Processes ==="
ps aux | grep -E "(python|gunicorn)" | grep -v grep || echo "No Python processes found"
EOF
}

view_logs() {
    echo -e "${BLUE}Viewing application logs...${NC}"
    check_config
    
    ssh "$SSH_CONFIG_ALIAS" << 'EOF'
echo "=== Recent logs ==="
find ~/app_ml_extractor -name "*.log" -exec tail -20 {} \; 2>/dev/null || echo "No log files found"
echo ""
echo "=== System logs (if accessible) ==="
tail -20 /var/log/messages 2>/dev/null || echo "System logs not accessible"
EOF
}

restart_app() {
    echo -e "${BLUE}Restarting application...${NC}"
    check_config
    
    ssh "$SSH_CONFIG_ALIAS" << 'EOF'
cd ~/app_ml_extractor
# Kill existing processes
pkill -f "gunicorn.*app" || true
pkill -f "python.*app" || true
sleep 2

# Start application
source .venv/bin/activate
nohup gunicorn -b 0.0.0.0:8000 app_improved:app > gunicorn.log 2>&1 &
echo "Application restarted"
EOF
}

upload_files() {
    echo -e "${BLUE}Uploading files to server...${NC}"
    check_config
    
    read -p "Enter local file/directory path: " local_path
    read -p "Enter remote path (relative to home): " remote_path
    
    if [[ -z "$remote_path" ]]; then
        remote_path="app_ml_extractor/"
    fi
    
    if [[ -d "$local_path" ]]; then
        rsync -avz -e "ssh" "$local_path/" "$SSH_CONFIG_ALIAS:$remote_path"
    else
        scp "$local_path" "$SSH_CONFIG_ALIAS:$remote_path"
    fi
    
    echo -e "${GREEN}Upload completed${NC}"
}

download_files() {
    echo -e "${BLUE}Downloading files from server...${NC}"
    check_config
    
    read -p "Enter remote file path (relative to home): " remote_path
    read -p "Enter local destination [./]: " local_path
    
    if [[ -z "$local_path" ]]; then
        local_path="./"
    fi
    
    scp -r "$SSH_CONFIG_ALIAS:$remote_path" "$local_path"
    echo -e "${GREEN}Download completed${NC}"
}

show_info() {
    echo -e "${BLUE}Server Configuration:${NC}"
    echo "Server: $SERVER_IP"
    echo "Username: $USERNAME"
    echo "SSH Key: $SSH_KEY_PATH"
    echo "Config Alias: $SSH_CONFIG_ALIAS"
    echo "Deploy Directory: $DEPLOY_DIR"
    echo ""
    echo -e "${BLUE}SSH Config Entry:${NC}"
    grep -A 8 "$SSH_CONFIG_ALIAS" "$HOME/.ssh/config" 2>/dev/null || echo "SSH config not found"
}

# Main script logic
case "${1:-help}" in
    setup)
        setup_ssh
        ;;
    test)
        test_connection
        ;;
    connect|ssh)
        connect_ssh
        ;;
    deploy)
        deploy_app
        ;;
    status)
        check_status
        ;;
    logs)
        view_logs
        ;;
    restart)
        restart_app
        ;;
    upload)
        upload_files
        ;;
    download)
        download_files
        ;;
    info)
        show_info
        ;;
    help|*)
        print_help
        ;;
esac
