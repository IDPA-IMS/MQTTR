$port = 8000
$currentPath = Get-Location
$folderName = Split-Path $currentPath -Leaf

clear

try
{
    $pythonCheck = python --version 2> $null
    if ($LASTEXITCODE -ne 0)
    {
        throw "Python not found."
    }
}
catch
{
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ and try again."
    exit 1
}

# Check if folder ends with ".controller"
if ($folderName -ne ".controller")
{
    Write-Host "This script must be run inside a folder named '$requiredSuffix'" -ForegroundColor Red
    Write-Host "Current folder: $folderName"
    exit 1
}

Write-Host "Starting web server..." -ForegroundColor Green
Write-Host "To stop the server hit 'ctrl'+'c'" -ForegroundColor Yellow
Write-Host ""

# Open browser
Start-Process "http://localhost:$port"

# Start Python HTTP server
python -m http.server $port

