$fileList = @("main.py", "gui.py", "api_classes.py", "XML_handler.py", "ViperBox.py", "VB_logger.py", "VB_classes.py")
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$mainFolderPath = Split-Path -Parent $scriptPath
foreach ($file in $fileList) {
    $fileUrl = "https://raw.githubusercontent.com/sbalk/viperboxinterface/dev/$file"
    $fileDestination = Join-Path -Path $mainFolderPath -ChildPath $file
    Invoke-WebRequest -Uri $fileUrl -OutFile $fileDestination
}
