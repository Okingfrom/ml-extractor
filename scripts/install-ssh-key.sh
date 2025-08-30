#!/bin/bash

# SSH Key Installation Script for ML-Extractor
# This script helps install your SSH public key on the server

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Your SSH public key
SSH_PUBLIC_KEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD8ERKPZSBbpCloqeZgcgxra8HvNaU3I2w7WtTkE8wmjFXlrUs60xlgOnX/lZrZJVn5WW0Y/cHWh2I75yRoOngZzHXXUrR/oovpBSi1IVrBp+q39mxyoR7riYod+ZxtBcfEPMaEHPWw4oClwzXvfmcErafvImCxfvPPY+5OWwSTjWowL/+c3rWfA9yP4hz5TxFTMRQ2vA9u9EQOVat8DIaPKhwnRHN0dy9vwqSyEl1plGDhfe/CddFInlmXQKpj0F74OconuezTfmbPa6KIT6a7A/+IiD+5zD0gV9oCYL7DaRKnr1pRsqoy+qiaFP+Ana2QhldTtvZoWXBEFuC35Kc1"

echo -e "${BLUE}ML-Extractor SSH Key Installation${NC}"
echo "=========================================="

if [[ $# -lt 2 ]]; then
    echo -e "${RED}Usage: $0 <username> <server_ip> [port]${NC}"
    echo ""
    echo "Examples:"
    echo "  $0 myuser myserver.com"
    echo "  $0 myuser 192.168.1.100 2222"
    exit 1
fi

USERNAME="$1"
SERVER_IP="$2"
PORT="${3:-22}"

echo -e "${YELLOW}Server: $USERNAME@$SERVER_IP:$PORT${NC}"
echo ""

# Create local SSH directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Save the public key locally
echo "$SSH_PUBLIC_KEY" > ~/.ssh/ml-extractor-key.pub
chmod 644 ~/.ssh/ml-extractor-key.pub

echo -e "${BLUE}Step 1: Testing connection to server...${NC}"
if ssh -p "$PORT" -o ConnectTimeout=10 -o BatchMode=yes "$USERNAME@$SERVER_IP" exit 2>/dev/null; then
    echo -e "${GREEN}✓ Connection successful${NC}"
else
    echo -e "${YELLOW}⚠ Connection requires authentication${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Installing SSH key on server...${NC}"

# Try to copy the SSH key
if command -v ssh-copy-id >/dev/null 2>&1; then
    echo "Using ssh-copy-id..."
    if ssh-copy-id -p "$PORT" -i ~/.ssh/ml-extractor-key.pub "$USERNAME@$SERVER_IP"; then
        echo -e "${GREEN}✓ SSH key installed successfully${NC}"
    else
        echo -e "${YELLOW}⚠ ssh-copy-id failed, trying manual installation...${NC}"
        manual_install=true
    fi
else
    echo "ssh-copy-id not available, using manual installation..."
    manual_install=true
fi

# Manual installation if ssh-copy-id failed or not available
if [[ "${manual_install:-false}" == "true" ]]; then
    echo ""
    echo -e "${YELLOW}Manual installation method:${NC}"
    echo "Please run this command on your server:"
    echo ""
    echo -e "${GREEN}mkdir -p ~/.ssh && chmod 700 ~/.ssh${NC}"
    echo -e "${GREEN}echo '$SSH_PUBLIC_KEY' >> ~/.ssh/authorized_keys${NC}"
    echo -e "${GREEN}chmod 600 ~/.ssh/authorized_keys${NC}"
    echo ""
    echo "Or connect to your server and run:"
    
    cat << 'EOF'
ssh USERNAME@SERVER_IP << 'REMOTE_SCRIPT'
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD8ERKPZSBbpCloqeZgcgxra8HvNaU3I2w7WtTkE8wmjFXlrUs60xlgOnX/lZrZJVn5WW0Y/cHWh2I75yRoOngZzHXXUrR/oovpBSi1IVrBp+q39mxyoR7riYod+ZxtBcfEPMaEHPWw4oClwzXvfmcErafvImCxfvPPY+5OWwSTjWowL/+c3rWfA9yP4hz5TxFTMRQ2vA9u9EQOVat8DIaPKhwnRHN0dy9vwqSyEl1plGDhfe/CddFInlmXQKpj0F74OconuezTfmbPa6KIT6a7A/+IiD+5zD0gV9oCYL7DaRKnr1pRsqoy+qiaFP+Ana2QhldTtvZoWXBEFuC35Kc1' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo "SSH key installed successfully"
REMOTE_SCRIPT
EOF
fi

echo ""
echo -e "${BLUE}Step 3: Testing key-based authentication...${NC}"
if ssh -p "$PORT" -o ConnectTimeout=10 -o PreferredAuthentications=publickey -o PasswordAuthentication=no "$USERNAME@$SERVER_IP" "echo 'SSH key authentication successful!'" 2>/dev/null; then
    echo -e "${GREEN}✓ SSH key authentication working!${NC}"
    
    # Create SSH config entry
    echo ""
    echo -e "${BLUE}Step 4: Creating SSH config entry...${NC}"
    SSH_CONFIG="$HOME/.ssh/config"
    
    if ! grep -q "ml-extractor-prod" "$SSH_CONFIG" 2>/dev/null; then
        cat >> "$SSH_CONFIG" << EOF

# ML-Extractor Production Server
Host ml-extractor-prod
    HostName $SERVER_IP
    User $USERNAME
    Port $PORT
    IdentityFile ~/.ssh/ml-extractor-key
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
EOF
        chmod 600 "$SSH_CONFIG"
        echo -e "${GREEN}✓ SSH config entry created${NC}"
        echo ""
        echo -e "${BLUE}You can now connect using:${NC}"
        echo -e "${GREEN}ssh ml-extractor-prod${NC}"
    else
        echo -e "${YELLOW}SSH config entry already exists${NC}"
    fi
    
else
    echo -e "${YELLOW}⚠ Key-based authentication not working yet${NC}"
    echo "Please ensure the SSH key is properly installed on the server"
fi

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Test connection: ssh ml-extractor-prod"
echo "2. Update SSH helper scripts with your server details"
echo "3. Run deployment: ./scripts/ssh-helper.sh deploy"
echo ""
echo -e "${GREEN}Setup completed!${NC}"
