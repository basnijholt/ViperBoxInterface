@echo off
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0\install_dependencies.ps1'"
cmd \k
