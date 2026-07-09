#!/usr/bin/env bash
# Usage: ./push_to_github.sh <remote_url> [branch]
set -euo pipefail
REMOTE_URL=${1:-}
BRANCH=${2:-main}

if [ -z "$REMOTE_URL" ]; then
  echo "Usage: $0 <remote_url> [branch]"
  exit 1
fi

# Initialize git if needed
if [ ! -d .git ]; then
  echo "Initializing git repository..."
  git init
  git add -A
  git commit -m "Initial commit: deploy website"
else
  echo "Git repository exists."
fi

# Add or set remote
if git remote get-url origin >/dev/null 2>&1; then
  echo "Remote 'origin' exists. Updating URL to $REMOTE_URL"
  git remote set-url origin "$REMOTE_URL"
else
  echo "Adding remote origin $REMOTE_URL"
  git remote add origin "$REMOTE_URL"
fi

# Ensure branch exists locally
if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  echo "Branch $BRANCH exists locally."
else
  echo "Creating branch $BRANCH"
  git checkout -b "$BRANCH"
fi

# Push
echo "Pushing to $REMOTE_URL (branch: $BRANCH). You may be prompted for credentials."
# Use --set-upstream so future pushes are simple
git push -u origin "$BRANCH"

echo "Push complete. Visit your GitHub repository to confirm."