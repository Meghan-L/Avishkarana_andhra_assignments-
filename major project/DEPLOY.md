Vercel Deployment Guide
======================

This project serves a static site from the `website/` directory. Use the steps below to push the repo to GitHub and connect it to Vercel.

1) Initialize git (if not already):

```bash
git init
git add .
git commit -m "Initial site for Vercel"
```

2) Create a GitHub repository (via web UI) and push:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

3) Deploy with Vercel (dashboard):
- Go to https://vercel.com and sign in (GitHub/GitLab/Bitbucket).
- Click "New Project" → Import your repository.
- Set the root or output directory to `website/` (if prompted).
- Vercel will detect a static site and deploy; you'll get a public URL.

4) Or deploy with Vercel CLI:

Install CLI:
```bash
npm i -g vercel
# or: corepack pnpm add -g vercel
```
Link & deploy:
```bash
cd "D:/avishkarana_andhra_assignments/major project"
vercel login
vercel link # choose or create a project
vercel --prod --confirm
```

Notes
- `vercel.json` is included and routes `/` to `/website/index.html`.
- If you want a custom domain, configure it in the Vercel dashboard.

Helper scripts
--------------
Two helper scripts are provided in `scripts/` to make pushing to GitHub easier from this machine:

- `scripts/push_to_github.sh` — Bash script for macOS/Linux/Git Bash/WSL
- `scripts/push_to_github.ps1` — PowerShell script for Windows

Usage example (PowerShell):
```powershell
\scripts\push_to_github.ps1 -RemoteUrl "https://github.com/your-username/your-repo.git" -Branch main
```

Usage example (bash):
```bash
./scripts/push_to_github.sh https://github.com/your-username/your-repo.git main
```

These scripts will initialize a git repo if one does not exist, create an initial commit, add or update the `origin` remote, and push the selected branch.
