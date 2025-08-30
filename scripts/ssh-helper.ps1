# SSH Connection Helper for ML-Extractor Deployment (PowerShell)
# This script helps manage SSH connections to your cPanel/hosting server

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Configuration (update these values)
$ServerIP = ""
$Username = ""
$SSHKeyPath = "$env:USERPROFILE\.ssh\ml-extractor-key"
$DeployDir = "app_ml_extractor"
$SSHConfigAlias = "ml-extractor-prod"

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

function Show-Help {
    Write-ColorText "ML-Extractor SSH Connection Helper (PowerShell)" "Blue"
    Write-Host ""
    Write-Host "Usage: .\ssh-helper.ps1 [command]"
    Write-Host ""
    Write-Host "Commands:"
    Write-ColorText "  setup        Setup SSH configuration" "Green"
    Write-ColorText "  test         Test SSH connection" "Green"
    Write-ColorText "  connect      Connect to server" "Green"
    Write-ColorText "  deploy       Deploy application" "Green"
    Write-ColorText "  status       Check application status" "Green"
    Write-ColorText "  logs         View application logs" "Green"
    Write-ColorText "  restart      Restart application" "Green"
    Write-ColorText "  upload       Upload local files to server" "Green"
    Write-ColorText "  download     Download files from server" "Green"
    Write-ColorText "  info         Show server information" "Green"
    Write-Host ""
}

function Test-Config {
    if ([string]::IsNullOrEmpty($ServerIP) -or [string]::IsNullOrEmpty($Username)) {
        Write-ColorText "Error: Server configuration not set!" "Red"
        Write-Host "Please edit this script and set `$ServerIP and `$Username variables."
        Write-Host "Example:"
        Write-Host '  $ServerIP = "your-server.com"'
        Write-Host '  $Username = "your-cpanel-username"'
        exit 1
    }
}

function Setup-SSH {
    Write-ColorText "Setting up SSH configuration..." "Blue"
    
    # Check if SSH directory exists
    $SSHDir = "$env:USERPROFILE\.ssh"
    if (!(Test-Path $SSHDir)) {
        New-Item -ItemType Directory -Path $SSHDir -Force | Out-Null
    }
    
    # Check if SSH key exists
    if (!(Test-Path $SSHKeyPath)) {
        Write-ColorText "SSH key not found. Generating new key..." "Yellow"
        $email = Read-Host "Enter your email for SSH key"
        ssh-keygen -t ed25519 -C $email -f $SSHKeyPath
        Write-ColorText "SSH key generated: $SSHKeyPath" "Green"
    }
    
    # Create SSH config entry
    $SSHConfig = "$env:USERPROFILE\.ssh\config"
    if (!(Test-Path $SSHConfig) -or !(Select-String -Path $SSHConfig -Pattern $SSHConfigAlias -Quiet)) {
        Write-ColorText "Adding SSH config entry..." "Yellow"
        
        $configEntry = @"

# ML-Extractor Production Server
Host $SSHConfigAlias
    HostName $ServerIP
    User $Username
    Port 22
    IdentityFile $SSHKeyPath
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
"@
        Add-Content -Path $SSHConfig -Value $configEntry
        Write-ColorText "SSH config entry added" "Green"
    }
    
    Write-ColorText "Next steps:" "Blue"
    Write-Host "1. Copy your public key to the server:"
    Write-Host "   ssh-copy-id -i $SSHKeyPath.pub $SSHConfigAlias"
    Write-Host "2. Or manually add this public key to your server:"
    if (Test-Path "$SSHKeyPath.pub") {
        Write-ColorText (Get-Content "$SSHKeyPath.pub") "Yellow"
    }
}

function Test-Connection {
    Write-ColorText "Testing SSH connection..." "Blue"
    Test-Config
    
    try {
        $result = ssh -o ConnectTimeout=10 $SSHConfigAlias "echo 'Connection successful!'" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ SSH connection successful" "Green"
            return $true
        } else {
            throw "Connection failed"
        }
    } catch {
        Write-ColorText "✗ SSH connection failed" "Red"
        Write-Host "Try: ssh-copy-id -i $SSHKeyPath.pub $SSHConfigAlias"
        return $false
    }
}

function Connect-SSH {
    Write-ColorText "Connecting to server..." "Blue"
    Test-Config
    ssh $SSHConfigAlias
}

function Deploy-App {
    Write-ColorText "Deploying application..." "Blue"
    Test-Config
    
    if (!(Test-Connection)) {
        Write-ColorText "Cannot deploy: SSH connection failed" "Red"
        exit 1
    }
    
    Write-ColorText "Running deployment script..." "Yellow"
    if (Test-Path ".\scripts\deploy_to_server.sh") {
        bash .\scripts\deploy_to_server.sh
    } else {
        Write-ColorText "Deployment script not found" "Red"
        return
    }
    Write-ColorText "Deployment completed" "Green"
}

function Check-Status {
    Write-ColorText "Checking application status..." "Blue"
    Test-Config
    
    $script = @'
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
'@
    
    ssh $SSHConfigAlias $script
}

function View-Logs {
    Write-ColorText "Viewing application logs..." "Blue"
    Test-Config
    
    $script = @'
echo "=== Recent logs ==="
find ~/app_ml_extractor -name "*.log" -exec tail -20 {} \; 2>/dev/null || echo "No log files found"
echo ""
echo "=== System logs (if accessible) ==="
tail -20 /var/log/messages 2>/dev/null || echo "System logs not accessible"
'@
    
    ssh $SSHConfigAlias $script
}

function Restart-App {
    Write-ColorText "Restarting application..." "Blue"
    Test-Config
    
    $script = @'
cd ~/app_ml_extractor
# Kill existing processes
pkill -f "gunicorn.*app" || true
pkill -f "python.*app" || true
sleep 2

# Start application
source .venv/bin/activate
nohup gunicorn -b 0.0.0.0:8000 app_improved:app > gunicorn.log 2>&1 &
echo "Application restarted"
'@
    
    ssh $SSHConfigAlias $script
}

function Upload-Files {
    Write-ColorText "Uploading files to server..." "Blue"
    Test-Config
    
    $localPath = Read-Host "Enter local file/directory path"
    $remotePath = Read-Host "Enter remote path (relative to home) [app_ml_extractor/]"
    
    if ([string]::IsNullOrEmpty($remotePath)) {
        $remotePath = "app_ml_extractor/"
    }
    
    if (Test-Path $localPath -PathType Container) {
        # Directory upload
        scp -r $localPath/* "${SSHConfigAlias}:$remotePath"
    } else {
        # File upload
        scp $localPath "${SSHConfigAlias}:$remotePath"
    }
    
    Write-ColorText "Upload completed" "Green"
}

function Download-Files {
    Write-ColorText "Downloading files from server..." "Blue"
    Test-Config
    
    $remotePath = Read-Host "Enter remote file path (relative to home)"
    $localPath = Read-Host "Enter local destination [./]"
    
    if ([string]::IsNullOrEmpty($localPath)) {
        $localPath = "./"
    }
    
    scp -r "${SSHConfigAlias}:$remotePath" $localPath
    Write-ColorText "Download completed" "Green"
}

function Show-Info {
    Write-ColorText "Server Configuration:" "Blue"
    Write-Host "Server: $ServerIP"
    Write-Host "Username: $Username"
    Write-Host "SSH Key: $SSHKeyPath"
    Write-Host "Config Alias: $SSHConfigAlias"
    Write-Host "Deploy Directory: $DeployDir"
    Write-Host ""
    Write-ColorText "SSH Config Entry:" "Blue"
    $configPath = "$env:USERPROFILE\.ssh\config"
    if (Test-Path $configPath) {
        $content = Get-Content $configPath | Out-String
        if ($content -match "Host $SSHConfigAlias(.*?)(?=Host|\z)") {
            Write-Host $matches[0]
        } else {
            Write-Host "SSH config not found"
        }
    } else {
        Write-Host "SSH config file not found"
    }
}

# Main script logic
switch ($Command.ToLower()) {
    "setup" { Setup-SSH }
    "test" { Test-Connection }
    "connect" { Connect-SSH }
    "ssh" { Connect-SSH }
    "deploy" { Deploy-App }
    "status" { Check-Status }
    "logs" { View-Logs }
    "restart" { Restart-App }
    "upload" { Upload-Files }
    "download" { Download-Files }
    "info" { Show-Info }
    default { Show-Help }
}
