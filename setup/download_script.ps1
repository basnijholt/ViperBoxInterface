$downloadUrl = "https://github.com/sbalk/ViperBoxInterface/archive/dev.zip"
$downloadPath = "$env:USERPROFILE\Downloads\viperboxinterface.zip"
$extractPath = "$env:USERPROFILE\Downloads\ViperBoxInterface"

# Download the ViperBoxInterface
Invoke-WebRequest -Uri $downloadUrl -OutFile $downloadPath

# Extract the downloaded file
Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force

# Run the installation script
$scriptPath = Join-Path -Path $extractPath -ChildPath "ViperBoxInterface-dev\setup\installation_script.ps1"
Start-Process -FilePath "powershell.exe" -ArgumentList "-File `"$scriptPath`"" -Wait
