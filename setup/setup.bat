@echo off
PowerShell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '%~dp0\setup\installation_script.ps1'"
cmd \k
