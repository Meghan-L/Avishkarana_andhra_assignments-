#!/bin/bash
set -e
cd "$(dirname "$0")/.."

git init
git add .
git commit -m "Initial bank fraud detection project"

if [ -z "$1" ]; then
  echo "Usage: $0 <git-remote-url>"
  exit 1
fi

git remote add origin "$1"
git branch -M main
git push -u origin main
