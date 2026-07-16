Set-StrictMode -Version Latest
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root\..

git init
git add .
git commit -m "Initial bank fraud detection project"

if (-not $args[0]) {
    Write-Host "Usage: .\push_to_github.ps1 <git-remote-url>"
    exit 1
}

git remote add origin $args[0]
git branch -M main
git push -u origin main
