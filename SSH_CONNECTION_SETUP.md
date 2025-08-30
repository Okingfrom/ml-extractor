# SSH Connection Configuration for ML-Extractor Deployment

## SSH Connection Setup

### 1. SSH Key Generation (if not already done)
```bash
# Generate new SSH key pair
ssh-keygen -t rsa -b 4096 -C "your-email@example.com" -f ~/.ssh/ml-extractor-key

# Or use Ed25519 (recommended)
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/ml-extractor-key
```

### 2. SSH Config File Setup
Create or edit `~/.ssh/config`:

```bash
# ML-Extractor Production Server
Host ml-extractor-prod
    HostName [YOUR_SERVER_IP_OR_DOMAIN]
    User [YOUR_CPANEL_USERNAME]
    Port 22
    IdentityFile ~/.ssh/ml-extractor-key
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes

# Alternative with password authentication (less secure)
Host ml-extractor-prod-pass
    HostName [YOUR_SERVER_IP_OR_DOMAIN]
    User [YOUR_CPANEL_USERNAME]
    Port 22
    PreferredAuthentications password
    PasswordAuthentication yes
```

### 3. Connection Commands

#### Quick Connection
```bash
# Using SSH config alias
ssh ml-extractor-prod

# Direct connection with key
ssh -i ~/.ssh/ml-extractor-key [USERNAME]@[SERVER_IP]

# Direct connection with password
ssh [USERNAME]@[SERVER_IP]
```

#### File Transfer (SCP/RSYNC)
```bash
# Upload files using SCP
scp -i ~/.ssh/ml-extractor-key file.txt ml-extractor-prod:~/

# Upload directory using RSYNC
rsync -avz -e "ssh -i ~/.ssh/ml-extractor-key" ./local-dir/ ml-extractor-prod:~/remote-dir/

# Download files
scp -i ~/.ssh/ml-extractor-key ml-extractor-prod:~/remote-file.txt ./
```

### 4. cPanel Terminal Access
Some cPanel hosts provide terminal access through:
- **cPanel Terminal**: File Manager → Terminal (web-based)
- **SSH/Shell Access**: Enable in cPanel → SSH Access
- **JetBackup Terminal**: Some hosts provide SSH through backup tools

### 5. Required Server Information

Please provide the following information:

```
Server Details:
- Server IP/Domain: ___________________
- SSH Port: _____________________ (usually 22)
- Username: _____________________
- Authentication Method: [SSH Key / Password]
- cPanel URL: ___________________
- Home Directory Path: ___________
```

### 6. Deployment Connection Test

```bash
# Test connection
ssh ml-extractor-prod "echo 'Connection successful!'"

# Test deployment directory
ssh ml-extractor-prod "ls -la ~/app_ml_extractor"

# Check Python availability
ssh ml-extractor-prod "which python3 && python3 --version"

# Check disk space
ssh ml-extractor-prod "df -h ~"
```

### 7. Automated Deployment with SSH

```bash
# Deploy from local machine
./scripts/deploy_to_server.sh

# Or deploy remotely via SSH
ssh ml-extractor-prod "cd ~/app_ml_extractor && git pull origin main && source .venv/bin/activate && pip install -r requirements.txt"
```

### 8. cPanel Integration

For cPanel deployments, the project includes:
- `.cpanel.yml` - Automatic deployment configuration
- `passenger_wsgi.py` - WSGI entry point for Passenger
- `scripts/deploy_to_server.sh` - Manual deployment script

### 9. Security Best Practices

```bash
# Set proper SSH key permissions
chmod 600 ~/.ssh/ml-extractor-key
chmod 644 ~/.ssh/ml-extractor-key.pub
chmod 700 ~/.ssh
chmod 600 ~/.ssh/config

# Add public key to server
ssh-copy-id -i ~/.ssh/ml-extractor-key.pub ml-extractor-prod
```

### 10. Troubleshooting

#### Connection Issues
```bash
# Verbose SSH connection for debugging
ssh -v ml-extractor-prod

# Test SSH key authentication
ssh -i ~/.ssh/ml-extractor-key -o PreferredAuthentications=publickey ml-extractor-prod

# Check SSH service
ssh ml-extractor-prod "sudo systemctl status ssh"
```

#### Permission Issues
```bash
# Fix file permissions on server
ssh ml-extractor-prod "chmod -R 755 ~/app_ml_extractor"

# Fix Python virtual environment
ssh ml-extractor-prod "cd ~/app_ml_extractor && python3 -m venv .venv --clear"
```

## Next Steps

1. **Provide server details** (IP, username, etc.)
2. **Choose authentication method** (SSH key recommended)
3. **Test connection** using the commands above
4. **Run deployment** using the configured SSH connection

Once you provide the server information, I can create a customized connection script for your specific setup.
