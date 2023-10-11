@echo off

if not exist "C:\Users\%USERNAME%\.ssh\" (
    mkdir "C:\Users\%USERNAME%\.ssh\"
    copy "known_hosts" "C:\Users\%USERNAME%\.ssh\"
    copy "known_hosts.old" "C:\Users\%USERNAME%\.ssh\"
    copy "deploy_viperbox_user" "C:\Users\%USERNAME%\.ssh\"
)

if not exist "C:\Users\%USERNAME%\.ssh\known_hosts" (
    copy "known_hosts" "C:\Users\%USERNAME%\.ssh\"
    copy "known_hosts.old" "C:\Users\%USERNAME%\.ssh\"
    copy "deploy_viperbox_user" "C:\Users\%USERNAME%\.ssh\"
) else (
    type "known_hosts" >> "C:\Users\%USERNAME%\.ssh\"
    type "known_hosts.old" >> "C:\Users\%USERNAME%\.ssh\"
    copy "deploy_viperbox_user" "C:\Users\%USERNAME%\.ssh\"
)

if not exist "C:\Users\%USERNAME%\.ssh\config" (
(
echo Host github.com
echo IdentityFile "C:\Users\%USERNAME%\.ssh\deploy_viperbox_user"
) 1> "C:\Users\%USERNAME%\.ssh\config"
)