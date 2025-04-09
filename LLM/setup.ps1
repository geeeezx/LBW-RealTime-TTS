Write-Host "Setting up Qwen streaming text generation environment with uv..." -ForegroundColor Green

# Check if uv is installed
$uvExists = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uvExists) {
    Write-Host "uv not detected, installing..." -ForegroundColor Yellow
    $tempDir = Join-Path $PWD "uv-temp"
    $zipPath = Join-Path $PWD "uv.zip"
    
    Invoke-WebRequest -Uri "https://github.com/astral-sh/uv/releases/download/0.1.21/uv-x86_64-pc-windows-msvc.zip" -OutFile $zipPath
    Expand-Archive -Path $zipPath -DestinationPath $tempDir -Force
    
    # Create a bin directory if it doesn't exist
    $binDir = Join-Path $PWD "bin"
    if (-not (Test-Path $binDir)) {
        New-Item -ItemType Directory -Path $binDir | Out-Null
    }
    
    Move-Item -Path (Join-Path $tempDir "uv.exe") -Destination $binDir -Force
    Remove-Item -Path $tempDir -Recurse -Force
    Remove-Item -Path $zipPath -Force
    
    Write-Host "uv has been installed to: $binDir" -ForegroundColor Green
    
    # Add to path for this session
    $env:PATH = "$binDir;" + $env:PATH
} else {
    Write-Host "uv detected..." -ForegroundColor Green
}

# Create virtual environment
$venvPath = Join-Path $PWD ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & uv venv
} else {
    Write-Host "Virtual environment already exists..." -ForegroundColor Green
}

# Activate virtual environment and install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
. $activateScript

# Install requirements
& uv pip install -r requirements.txt

Write-Host "`nSetup complete!" -ForegroundColor Green
Write-Host "You can start the service with:" -ForegroundColor Cyan
Write-Host "python main.py" -ForegroundColor White 