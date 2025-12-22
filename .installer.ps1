$ErrorActionPreference = 'Stop'
# Setup script. Checks, installs and sets up all requirements

try
{
    # Check if running as Administrator
    $IsAdmin = ([Security.Principal.WindowsPrincipal] `
        [Security.Principal.WindowsIdentity]::GetCurrent()
    ).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)

    if (-not $IsAdmin)
    {
        Write-Warning "This script is not running with Administrator privileges. Please run as admin"
        exit 1
    }

    Write-Host "Running with Administrator rights." -ForegroundColor Green
    Write-Host "Checking for Python installation..."

    $python = Get-Command python -ErrorAction SilentlyContinue

    if ($null -eq $python)
    {
        Write-Warning "Python is not installed. Installing Python using WinGet..."

        if (-not (Get-Command winget -ErrorAction SilentlyContinue))
        {
            throw "WinGet is not installed. Please install WinGet manually."
        }

        winget install Python.Python.3 --accept-package-agreements --accept-source-agreements

        if ($LASTEXITCODE -ne 0)
        {
            throw "Python installation failed. Exit code: $LASTEXITCODE"
        }

        Write-Host "Python installation completed successfully." -ForegroundColor Green
    }
    else
    {
        Write-Host "Python is already installed at: $( $python.Source )" -ForegroundColor Green
    }

    Write-Host "Checking for Mosquitto installation..."

    $mosqDir = "C:\Program Files\mosquitto"
    $mosqExe = Join-Path $mosqDir "mosquitto.exe"

    $mosqCmd = Get-Command mosquitto.exe -ErrorAction SilentlyContinue
    $mosqInstalled = $mosqCmd -or (Test-Path $mosqExe)

    if (-not $mosqInstalled)
    {

        Write-Warning "Mosquitto is NOT installed. Installing with WinGet..."

        if (-not (Get-Command winget -ErrorAction SilentlyContinue))
        {
            throw "WinGet is not installed. Please install WinGet manually."
        }

        winget install EclipseFoundation.Mosquitto --accept-package-agreements --accept-source-agreements

        if ($LASTEXITCODE -ne 0)
        {
            throw "Mosquitto installation failed. Exit code: $LASTEXITCODE"
        }

        Write-Host "Mosquitto installed successfully." -ForegroundColor Green
    }
    else
    {
        Write-Host "Mosquitto already installed successfully." -ForegroundColor Green
    }

    if (-not (Test-Path $mosqDir))
    {
        throw "Mosquitto directory not found - installation may be unusual."
    }

    Set-Location $mosqDir
    Write-Host "Creating Mosquitto configuration file..." -ForegroundColor Cyan

    $confPath = Join-Path $mosqDir "mosquitto.conf"

    $confContent = @"
listener 1883 0.0.0.0

listener 8081
protocol websockets

allow_anonymous true
"@

    Set-Content -Path $confPath -Value $confContent -Encoding ASCII -Force
    Write-Host "mosquitto.conf created successfully." -ForegroundColor Green

    Write-Host "Configuring Windows Firewall for MQTT (TCP 1883)..." -ForegroundColor Cyan

    $fwRuleNameIn = "Mosquitto MQTT Inbound 1883"
    $fwRuleNameOut = "Mosquitto MQTT Outbound 1883"

    if (-not (Get-NetFirewallRule -DisplayName $fwRuleNameIn -ErrorAction SilentlyContinue))
    {
        New-NetFirewallRule `
            -DisplayName $fwRuleNameIn `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort 1883 `
            -Action Allow `
            -Profile Any
    }

    if (-not (Get-NetFirewallRule -DisplayName $fwRuleNameOut -ErrorAction SilentlyContinue))
    {
        New-NetFirewallRule `
            -DisplayName $fwRuleNameOut `
            -Direction Outbound `
            -Protocol TCP `
            -RemotePort 1883 `
            -Action Allow `
            -Profile Any
    }

    Write-Host "Starting Mosquitto..." -ForegroundColor Cyan

    Start-Process powershell.exe `
        -Verb RunAs `
        -WorkingDirectory $mosqDir `
        -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-Command .\mosquitto.exe -v -c .\mosquitto.conf"

    $desktopPath = [Environment]::GetFolderPath("Desktop")
    Set-Location $desktopPath

    if (-not (Get-Command git -ErrorAction SilentlyContinue))
    {
        throw "Git is not installed. Please install Git and re-run the script."
    }

    $repoUrl = "https://github.com/IDPA-IMS/MQTTR.git"
    $repoDir = Join-Path $desktopPath "MQTTR"

    if (-not (Test-Path $repoDir))
    {
        git clone $repoUrl
        if ($LASTEXITCODE -ne 0)
        {
            throw "Git clone failed."
        }
    }

    explorer.exe $repoDir

    $controllerDir = Join-Path $repoDir ".controller"

    if (-not (Test-Path $controllerDir))
    {
        throw ".controller directory not found."
    }

    Start-Process powershell.exe `
        -Verb RunAs `
        -WorkingDirectory $controllerDir `
        -ArgumentList "-NoExit", "-ExecutionPolicy Bypass", "-Command .\startup.ps1"

    Write-Host "All setup steps completed successfully." -ForegroundColor Green
}
catch
{
    Write-Host "A general failure occurred." -ForegroundColor Red
    Write-Host "Are you running this as admin?" -ForegroundColor Red
    exit 1
}
