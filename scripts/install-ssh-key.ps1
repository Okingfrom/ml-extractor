# SSH Key Installation Script for ML-Extractor (PowerShell)
# This script helps install your SSH public key on the server

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$Username,
    
    [Parameter(Mandatory=$true, Position=1)]
    [string]$ServerIP,
    
    [Parameter(Position=2)]
    [int]$Port = 22
)

# Your SSH public key
$SSHPublicKey = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQD8ERKPZSBbpCloqeZgcgxra8HvNaU3I2w7WtTkE8wmjFXlrUs60xlgOnX/lZrZJVn5WW0Y/cHWh2I75yRoOngZzHXXUrR/oovpBSi1IVrBp+q39mxyoR7riYod+ZxtBcfEPMaEHPWw4oClwzXvfmcErafvImCxfvPPY+5OWwSTjWowL/+c3rWfA9yP4hz5TxFTMRQ2vA9u9EQOVat8DIaPKhwnRHN0dy9vwqSyEl1plGDhfe/CddFInlmXQKpj0F74OconuezTfmbPa6KIT6a7A/+IiD+5zD0gV9oCYL7DaRKnr1pRsqoy+qiaFP+Ana2QhldTtvZoWXBEFuC35Kc1"

function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

Write-ColorText "ML-Extractor SSH Key Installation" "Blue"
Write-Host "=========================================="

Write-ColorText "Server: $Username@$ServerIP`:$Port" "Yellow"
Write-Host ""

# Create local SSH directory if it doesn't exist
$SSHDir = "$env:USERPROFILE\.ssh"
if (!(Test-Path $SSHDir)) {
    New-Item -ItemType Directory -Path $SSHDir -Force | Out-Null
    Write-ColorText "Created SSH directory: $SSHDir" "Green"
}

# Save the public key locally
$PublicKeyPath = "$SSHDir\ml-extractor-key.pub"
$SSHPublicKey | Out-File -FilePath $PublicKeyPath -Encoding ASCII
Write-ColorText "✓ SSH public key saved locally" "Green"

Write-ColorText "Step 1: Testing connection to server..." "Blue"
try {
    $result = ssh -p $Port -o ConnectTimeout=10 -o BatchMode=yes "$Username@$ServerIP" "exit" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✓ Connection successful" "Green"
    } else {
        Write-ColorText "⚠ Connection requires authentication" "Yellow"
    }
} catch {
    Write-ColorText "⚠ Connection test failed" "Yellow"
}

Write-Host ""
Write-ColorText "Step 2: Installing SSH key on server..." "Blue"

# Try to use ssh-copy-id if available
$sshCopyIdAvailable = Get-Command ssh-copy-id -ErrorAction SilentlyContinue
if ($sshCopyIdAvailable) {
    Write-Host "Using ssh-copy-id..."
    try {
        ssh-copy-id -p $Port -i $PublicKeyPath "$Username@$ServerIP"
        if ($LASTEXITCODE -eq 0) {
            Write-ColorText "✓ SSH key installed successfully" "Green"
            $manualInstall = $false
        } else {
            Write-ColorText "⚠ ssh-copy-id failed, showing manual installation..." "Yellow"
            $manualInstall = $true
        }
    } catch {
        Write-ColorText "⚠ ssh-copy-id failed, showing manual installation..." "Yellow"
        $manualInstall = $true
    }
} else {
    Write-Host "ssh-copy-id not available, showing manual installation..."
    $manualInstall = $true
}

# Manual installation instructions
if ($manualInstall) {
    Write-Host ""
    Write-ColorText "Manual installation method:" "Yellow"
    Write-Host "Please run these commands on your server:"
    Write-Host ""
    Write-ColorText "mkdir -p ~/.ssh && chmod 700 ~/.ssh" "Green"
    Write-ColorText "echo '$SSHPublicKey' >> ~/.ssh/authorized_keys" "Green"
    Write-ColorText "chmod 600 ~/.ssh/authorized_keys" "Green"
    Write-Host ""
    Write-Host "Or connect to your server and run this single command:"
    Write-Host ""
    Write-ColorText "ssh $Username@$ServerIP" "Green"
    Write-Host "Then on the server:"
    Write-ColorText @"
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '$SSHPublicKey' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
echo 'SSH key installed successfully'
"@ "Green"
}

Write-Host ""
Write-ColorText "Step 3: Testing key-based authentication..." "Blue"
try {
    $result = ssh -p $Port -o ConnectTimeout=10 -o PreferredAuthentications=publickey -o PasswordAuthentication=no "$Username@$ServerIP" "echo 'SSH key authentication successful!'" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "✓ SSH key authentication working!" "Green"
        
        # Create SSH config entry
        Write-Host ""
        Write-ColorText "Step 4: Creating SSH config entry..." "Blue"
        $SSHConfig = "$SSHDir\config"
        
        $configExists = $false
        if (Test-Path $SSHConfig) {
            $configContent = Get-Content $SSHConfig | Out-String
            if ($configContent -match "ml-extractor-prod") {
                $configExists = $true
            }
        }
        
        if (!$configExists) {
            $configEntry = @"

# ML-Extractor Production Server
Host ml-extractor-prod
    HostName $ServerIP
    User $Username
    Port $Port
    IdentityFile ~/.ssh/ml-extractor-key
    IdentitiesOnly yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
"@
            Add-Content -Path $SSHConfig -Value $configEntry
            Write-ColorText "✓ SSH config entry created" "Green"
            Write-Host ""
            Write-ColorText "You can now connect using:" "Blue"
            Write-ColorText "ssh ml-extractor-prod" "Green"
        } else {
            Write-ColorText "SSH config entry already exists" "Yellow"
        }
        
    } else {
        Write-ColorText "⚠ Key-based authentication not working yet" "Yellow"
        Write-Host "Please ensure the SSH key is properly installed on the server"
    }
} catch {
    Write-ColorText "⚠ Key-based authentication test failed" "Yellow"
    Write-Host "Please ensure the SSH key is properly installed on the server"
}

Write-Host ""
Write-ColorText "Next steps:" "Blue"
Write-Host "1. Test connection: ssh ml-extractor-prod"
Write-Host "2. Update SSH helper scripts with your server details"
Write-Host "3. Run deployment: .\scripts\ssh-helper.ps1 deploy"
Write-Host ""
Write-ColorText "Setup completed!" "Green"
