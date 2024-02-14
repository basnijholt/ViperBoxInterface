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
$ProgressPreference = 'Continue'
foreach ($s in $software.GetEnumerator()) {
    if (Test-Path -Path $s.Value.checkPath) {
        Write-Host "$($s.Name) is already installed." -ForegroundColor Green
    } else {
        Write-Host "Installing $($s.Name)..." -ForegroundColor Yellow
        $installerPath = "$env:TEMP\$($s.Name).exe"
        Invoke-WebRequest -Uri $s.Value.url -OutFile $installerPath
        Start-Process -FilePath $installerPath -Wait -ArgumentList "/S /AddToPath=1"
        Remove-Item -Path $installerPath
        Write-Host "$($s.Name) has been installed." -ForegroundColor Green
    }
}

# Update the conda base environment and create a new environment
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$envYamlPath = Join-Path -Path $scriptPath -ChildPath "viperboxV0_0_1.yaml"
Write-Host "Creating a new Conda environment and installing packages..." -ForegroundColor Yellow
Start-Porcess -FilePath "C:\ProgramData\Anaconda3\Scripts\conda.exe" -ArgumentList "update -n base conda -y" -Wait
Start-Process -FilePath "C:\ProgramData\Anaconda3\Scripts\conda.exe" -ArgumentList "env create -f `"$envYamlPath`" -y" -Wait

# Create a startup file called start_app.bat that always starts in the right location
$mainFolderPath = Split-Path -Parent $scriptPath
$batchFilePath = Join-Path -Path $mainFolderPath -ChildPath "start_app.bat"
$batchContent = "@echo off`ncd /d `"%~dp0`"`ncall conda activate vb311`nuvicorn main:app --reload"
Set-Content -Path $batchFilePath -Value $batchContent

# Create shortcut on the desktop
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path -Path $desktopPath -ChildPath "ViperBoxAPI.lnk"
$iconPath = Join-Path -Path $scriptPath -ChildPath "\logo.ico"
# Create the shortcut
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $batchFilePath
$Shortcut.IconLocation = $iconPath
$Shortcut.Save()

Write-Host "All tasks completed!" -ForegroundColor Green

Read-Host -Prompt "Press Enter to exit"

