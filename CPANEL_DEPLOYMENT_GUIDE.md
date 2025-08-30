# 🚀 ML-Extractor cPanel Deployment Guide

## Pre-Deployment Checklist

### ✅ 1. Server Information Required
Please provide the following information:

```
🌐 Server Details:
- [ ] Server IP/Domain: _________________________
- [ ] SSH Port: _____________ (usually 22)
- [ ] cPanel Username: _________________________
- [ ] cPanel Password: _________________________
- [ ] cPanel URL: _________________________
- [ ] Home Directory: _________________________ (usually /home/username)

🔐 Authentication Method:
- [ ] SSH Key Authentication (recommended)
- [ ] Password Authentication
- [ ] cPanel Terminal Access
```

### ✅ 2. Local Setup
Before deployment, ensure you have:

- [ ] SSH client installed (Windows: OpenSSH, PuTTY, or WSL)
- [ ] Git configured with your repository access
- [ ] Server credentials available

### ✅ 3. Server Requirements Check
Your hosting server should have:

- [ ] Python 3.8+ available
- [ ] pip package manager
- [ ] Virtual environment support
- [ ] SSH/Terminal access
- [ ] Git access (for repository cloning)
- [ ] Required disk space (minimum 500MB)

## 🔧 Deployment Methods

### Method 1: Automatic cPanel Deployment
If your hosting supports cPanel Git deployment:

1. **Enable Git in cPanel**
   - Go to cPanel → Git Version Control
   - Create repository: `https://github.com/Okingfrom/ml-extractor.git`
   - Set deployment path: `public_html/ml-extractor` or custom directory

2. **Configure Passenger**
   - The `.cpanel.yml` file will handle automatic deployment
   - Passenger will use `passenger_wsgi.py` as entry point

### Method 2: SSH Manual Deployment
Using the provided SSH helper scripts:

#### For Linux/Mac:
```bash
# 1. Setup SSH connection
./scripts/ssh-helper.sh setup

# 2. Test connection
./scripts/ssh-helper.sh test

# 3. Deploy application
./scripts/ssh-helper.sh deploy

# 4. Check status
./scripts/ssh-helper.sh status
```

#### For Windows (PowerShell):
```powershell
# 1. Setup SSH connection
.\scripts\ssh-helper.ps1 setup

# 2. Test connection
.\scripts\ssh-helper.ps1 test

# 3. Deploy application
.\scripts\ssh-helper.ps1 deploy

# 4. Check status
.\scripts\ssh-helper.ps1 status
```

### Method 3: Manual Terminal Deployment
If using cPanel Terminal or direct SSH:

```bash
# 1. Connect to server
ssh username@your-server.com

# 2. Clone repository
cd ~/
git clone https://github.com/Okingfrom/ml-extractor.git app_ml_extractor
cd app_ml_extractor

# 3. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your settings

# 5. Create necessary directories
mkdir -p uploads backups logs
chmod 755 uploads backups logs

# 6. Test application
python app_improved.py
```

## 🔧 SSH Connection Setup

### Step 1: Configure SSH Helper
Edit the SSH helper script with your server details:

**For Bash (ssh-helper.sh):**
```bash
# Update these values in scripts/ssh-helper.sh
SERVER_IP="your-server.com"
USERNAME="your-cpanel-username"
```

**For PowerShell (ssh-helper.ps1):**
```powershell
# Update these values in scripts/ssh-helper.ps1
$ServerIP = "your-server.com"
$Username = "your-cpanel-username"
```

### Step 2: Generate SSH Key (if needed)
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/ml-extractor-key

# Copy public key to server
ssh-copy-id -i ~/.ssh/ml-extractor-key.pub username@your-server.com
```

### Step 3: Test Connection
```bash
# Test SSH connection
ssh -i ~/.ssh/ml-extractor-key username@your-server.com "echo 'Success!'"
```

## 🌐 cPanel Configuration

### 1. Python App Setup (if supported)
Some cPanel hosts support Python apps:

- Go to cPanel → Setup Python App
- Python version: 3.8+
- Application root: `/app_ml_extractor`
- Application URL: Your desired subdomain/path
- Application startup file: `passenger_wsgi.py`

### 2. Environment Variables
Set these in cPanel or `.env` file:

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./ml_extractor.db
ALLOWED_ORIGINS=https://your-domain.com
```

### 3. File Permissions
Ensure proper permissions:

```bash
chmod 755 ~/app_ml_extractor
chmod 644 ~/app_ml_extractor/.cpanel.yml
chmod 644 ~/app_ml_extractor/passenger_wsgi.py
chmod -R 755 ~/app_ml_extractor/uploads
chmod -R 755 ~/app_ml_extractor/backups
```

## 🔄 Post-Deployment Steps

### 1. Verify Deployment
```bash
# Check application status
./scripts/ssh-helper.sh status

# View logs
./scripts/ssh-helper.sh logs

# Test application endpoints
curl https://your-domain.com/health
```

### 2. Configure Monitoring
Set up basic monitoring:

```bash
# Create a simple health check script
echo '#!/bin/bash
curl -f https://your-domain.com/health || echo "App down at $(date)"' > ~/health_check.sh
chmod +x ~/health_check.sh

# Add to crontab for monitoring
crontab -e
# Add: */5 * * * * ~/health_check.sh >> ~/health_check.log 2>&1
```

### 3. Backup Strategy
```bash
# Create backup script
echo '#!/bin/bash
cd ~/app_ml_extractor
tar -czf ~/backups/ml-extractor-$(date +%Y%m%d-%H%M%S).tar.gz . --exclude=.venv --exclude=*.log' > ~/backup.sh
chmod +x ~/backup.sh

# Schedule weekly backups
crontab -e
# Add: 0 2 * * 0 ~/backup.sh
```

## 🚨 Troubleshooting

### Common Issues:

1. **Permission Denied**
   ```bash
   chmod +x scripts/ssh-helper.sh
   chmod 755 ~/app_ml_extractor
   ```

2. **Python Module Not Found**
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   pkill -f gunicorn
   pkill -f python
   ```

4. **Database Issues**
   ```bash
   rm ml_extractor.db
   python -c "from backend.database import create_tables; create_tables()"
   ```

## 📞 Support Commands

Quick diagnostic commands:

```bash
# System info
./scripts/ssh-helper.sh info

# Check Python environment
ssh your-server "cd ~/app_ml_extractor && source .venv/bin/activate && python --version && pip list"

# Check running processes
ssh your-server "ps aux | grep python"

# Check disk space
ssh your-server "df -h ~"

# Check logs
ssh your-server "cd ~/app_ml_extractor && find . -name '*.log' -exec tail -10 {} \;"
```

## 🎯 Next Steps

Once you provide your server information, I can:

1. ✅ Customize the SSH helper scripts with your server details
2. ✅ Create a specific deployment command for your setup
3. ✅ Test the connection and deployment process
4. ✅ Provide server-specific troubleshooting

**Please provide your server details to continue with the customized setup!** 🚀
