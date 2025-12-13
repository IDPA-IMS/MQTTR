# Setup script. Checks, installs and sets up all requirements

# Check if running as Administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal] `
    [Security.Principal.WindowsIdentity]::GetCurrent()
).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)

if (-not $IsAdmin) {
    Write-Warning "This script is not running with Administrator privileges. Please run as admin"

    exit 1
}

Write-Host "Running with Administrator rights." -ForegroundColor Green

Write-Host "Checking for Python installation..."

$python = Get-Command python -ErrorAction SilentlyContinue

if ($null -eq $python) {
    Write-Warning "Python is not installed. Installing Python using WinGet..."

    # Make sure WinGet exists
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Error "WinGet is not installed. Please install WinGet manually."
        exit 1
    }

    # Install latest Python package from WinGet
    winget install -e --id Python.Python.3 --source winget --accept-package-agreements --accept-source-agreements

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Python installation completed successfully." -ForegroundColor Green
    } else {
        Write-Error "Python installation failed. Exit code: $LASTEXITCODE"
        exit 1
    }
}
else {
    Write-Host "Python is already installed at: $($python.Source)" -ForegroundColor Green
}


Write-Host "Checking for Mosquitto installation..."

# Expected install directory
$mosqDir = "C:\Program Files\mosquitto"
$mosqExe = Join-Path $mosqDir "mosquitto.exe"

# Check if mosquitto exists (PATH or install directory)
$mosqCmd = Get-Command mosquitto.exe -ErrorAction SilentlyContinue
$mosqInstalled = $mosqCmd -or (Test-Path $mosqExe)

if (-not $mosqInstalled) {

    Write-Warning "Mosquitto is NOT installed. Installing with WinGet..."

    # Ensure winget exists
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-Error "WinGet is not installed. Please install WinGet manually."
        exit 1
    }

    # Install Mosquitto
    winget install -e --id Eclipse.Mosquitto --source winget --accept-package-agreements --accept-source-agreements

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Mosquitto installation failed. Exit code: $LASTEXITCODE"
        exit 1
    }

    Write-Host "Mosquitto installed successfully." -ForegroundColor Green
}

Write-Host "Mosquitto already installed successfully." -ForegroundColor Green


# After install or if already installed, verify directory exists
if (Test-Path $mosqDir) {
    Write-Host "Navigating to Mosquitto directory: $mosqDir" -ForegroundColor Cyan
    Set-Location $mosqDir
} else {
    Write-Warning "Mosquitto directory not found — installation may be unusual."
    exit 1
}

Write-Host "Creating Mosquitto configuration file..." -ForegroundColor Cyan

$confPath = Join-Path $mosqDir "mosquitto.conf"

$confContent = @"
listener 1883 0.0.0.0

listener 8081
protocol websockets

allow_anonymous true
"@

try {
    Set-Content -Path $confPath -Value $confContent -Encoding ASCII -Force
    Write-Host "mosquitto.conf created successfully at $confPath" -ForegroundColor Green
} catch {
    Write-Error "Failed to create mosquitto.conf"
    exit 1
}


# Add Windows Firewall rules for MQTT (TCP 1883)
Write-Host "Configuring Windows Firewall for MQTT (TCP 1883)..." -ForegroundColor Cyan

$fwRuleNameIn  = "Mosquitto MQTT Inbound 1883"
$fwRuleNameOut = "Mosquitto MQTT Outbound 1883"

# Inbound rule
if (-not (Get-NetFirewallRule -DisplayName $fwRuleNameIn -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule `
        -DisplayName $fwRuleNameIn `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 1883 `
        -Action Allow `
        -Profile Any
}

# Outbound rule
if (-not (Get-NetFirewallRule -DisplayName $fwRuleNameOut -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule `
        -DisplayName $fwRuleNameOut `
        -Direction Outbound `
        -Protocol TCP `
        -RemotePort 1883 `
        -Action Allow `
        -Profile Any
}

Write-Host "Firewall rules for TCP 1883 are configured." -ForegroundColor Green


Write-Host "Starting Mosquitto in a new elevated PowerShell window..." -ForegroundColor Cyan

$startMosquittoCmd = @"
.\mosquitto.exe -v -c .\mosquitto.conf
"@

Start-Process powershell.exe `
    -Verb RunAs `
    -WorkingDirectory $mosqDir `
    -ArgumentList @(
        "-NoExit"
        "-ExecutionPolicy Bypass"
        "-Command $startMosquittoCmd"
    )

Write-Host "Navigating to Desktop..." -ForegroundColor Cyan

$desktopPath = [Environment]::GetFolderPath("Desktop")
Set-Location $desktopPath

# Ensure git exists
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed. Please install Git and re-run the script."
    exit 1
}

Write-Host "Cloning MQTTR repository..." -ForegroundColor Cyan

$repoUrl = "https://github.com/IDPA-IMS/MQTTR.git"
$repoDir = Join-Path $desktopPath "MQTTR"

if (-not (Test-Path $repoDir)) {
    git clone $repoUrl
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Git clone failed."
        exit 1
    }
} else {
    Write-Warning "MQTTR directory already exists. Skipping clone."
}

Write-Host "Opening repository in Explorer..." -ForegroundColor Cyan
explorer.exe $repoDir

# Move into .controller directory
$controllerDir = Join-Path $repoDir ".controller"

if (-not (Test-Path $controllerDir)) {
    Write-Error ".controller directory not found."
    exit 1
}

Write-Host "Launching startup.ps1 in a new elevated PowerShell window..." -ForegroundColor Cyan

$controllerCmd = @"
.\startup.ps1
"@

Start-Process powershell.exe `
    -Verb RunAs `
    -WorkingDirectory $controllerDir `
    -ArgumentList @(
        "-NoExit"
        "-ExecutionPolicy Bypass"
        "-Command $controllerCmd"
    )

Write-Host "All setup steps completed successfully." -ForegroundColor Green
