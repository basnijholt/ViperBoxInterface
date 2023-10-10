# PowerShell Script Example

# Ensure the script is running with administrative privileges
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Inform the user
Write-Host "Starting the installation process..." -ForegroundColor Cyan

# Define URLs and paths
$openEphysUrl = "https://openephysgui.jfrog.io/artifactory/Release-Installer/windows/Install-Open-Ephys-GUI-v0.6.6.exe"
$openEphysPath = "$env:TEMP\Install-Open-Ephys-GUI-v0.6.6.exe"
$anacondaUrl = "https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Windows-x86_64.exe"
$anacondaPath = "$env:TEMP\Anaconda3-2023.09-0-Windows-x86_64.exe"
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$envYamlPath = Join-Path -Path $scriptPath -ChildPath "environment.yml"

# Check and Install Open Ephys
if (-not (Test-Path "C:\Program Files\Open Ephys")) {
    Write-Host "Installing Open Ephys..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $openEphysUrl -OutFile $openEphysPath
    Start-Process -FilePath $openEphysPath -Wait -ArgumentList "/S"
} else {
    Write-Host "Open Ephys is already installed." -ForegroundColor Green
}

# Check and Install Anaconda
if (-not (Test-Path "C:\ProgramData\Anaconda3")) {
    Write-Host "Installing Anaconda..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $anacondaUrl -OutFile $anacondaPath
    Start-Process -FilePath $anacondaPath -Wait -ArgumentList "/S"
} else {
    Write-Host "Anaconda is already installed." -ForegroundColor Green
}

# Create a new Conda environment and install packages from environment.yaml
Write-Host "Creating a new Conda environment and installing packages..." -ForegroundColor Yellow
Start-Process -FilePath "C:\ProgramData\Anaconda3\Scripts\conda.exe" -ArgumentList "env create -f `"$envYamlPath`"" -Wait

# Inform the user of completion
Write-Host "Installation and setup completed! You can close this window." -ForegroundColor Green
