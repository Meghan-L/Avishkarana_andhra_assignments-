param(
  [Parameter(Mandatory=$true)][string]$RemoteUrl,
  [string]$Branch = 'main'
)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "git is not installed or not in PATH"
  exit 1
}

if (-not (Test-Path .git)) {
  Write-Host "Initializing git repository..."
  git init
  git add -A
  git commit -m "Initial commit: deploy website"
} else {
  Write-Host "Git repository already initialized."
}

# Add or update remote
try {
  git remote get-url origin > $null 2>&1
  Write-Host "Remote 'origin' exists. Updating URL to $RemoteUrl"
  git remote set-url origin $RemoteUrl
} catch {
  Write-Host "Adding remote 'origin' -> $RemoteUrl"
  git remote add origin $RemoteUrl
}

# Create branch if not exists
$branchExists = git show-ref --verify --quiet "refs/heads/$Branch"; if ($LASTEXITCODE -ne 0) { $branchExists = $false } else { $branchExists = $true }
if (-not $branchExists) {
  Write-Host "Creating branch $Branch"
  git checkout -b $Branch
} else {
  Write-Host "Branch $Branch exists locally."
}

Write-Host "Pushing to $RemoteUrl (branch: $Branch). You may be prompted for credentials."
git push -u origin $Branch
Write-Host "Push complete. Visit your GitHub repository to confirm."