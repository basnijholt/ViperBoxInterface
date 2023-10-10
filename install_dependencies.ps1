# Ensure the script is running with administrative privileges
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# Define URLs and paths for software installations
$software = @{
    "OpenEphys" = @{
        "url" = "https://openephysgui.jfrog.io/artifactory/Release-Installer/windows/Install-Open-Ephys-GUI-v0.6.6.exe"
        "checkPath" = "C:\Program Files\Open Ephys"
    }
    "Anaconda" = @{
        "url" = "https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Windows-x86_64.exe"
        "checkPath" = "C:\ProgramData\Anaconda3"
    }
    "Git" = @{
        "url" = "https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"
        "checkPath" = "C:\Program Files\Git"
    }
}

# Install the software
$ProgressPreference = 'SilentlyContinue'
foreach ($s in $software.GetEnumerator()) {
    if (Test-Path -Path $s.Value.checkPath) {
        Write-Host "$($s.Name) is already installed." -ForegroundColor Green
    } else {
        Write-Host "Installing $($s.Name)..." -ForegroundColor Yellow
        $installerPath = "$env:TEMP\$($s.Name).exe"
        Invoke-WebRequest -Uri $s.Value.url -OutFile $installerPath
        Start-Process -FilePath $installerPath -Wait -ArgumentList "/S"
        Remove-Item -Path $installerPath
    }
}

# Create and configure the Conda environment
if ((conda env list) -match 'neuraviper') {
    Write-Host "Conda environment 'neuraviper' already exists." -ForegroundColor Green
} else {
    Write-Host "Creating Conda environment 'neuraviper'..." -ForegroundColor Yellow
    conda create --name neuraviper --clone base
    conda activate neuraviper
    conda env update --file "$(Get-Location)\environment.yaml" --prune
}

Write-Host "All tasks completed!" -ForegroundColor Green
