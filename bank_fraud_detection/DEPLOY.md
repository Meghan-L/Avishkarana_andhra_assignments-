Vercel Deployment Guide
======================

This project serves a static site from the `website/` directory. Use the steps below to push the repo to GitHub and connect it to Vercel.

1) Initialize git (if not already):

```bash
git init
git add .
git commit -m "Initial site for Vercel"
```

2) Create a GitHub repository and push:

```bash
git remote add origin https://github.com/<your-username>/<repo-name>.git
git branch -M main
git push -u origin main
```

3) Deploy with Vercel (dashboard):
- Go to https://vercel.com and sign in.
- Click "New Project" → Import your repository.
- Set the root or output directory to `website/` if prompted.
- Vercel will detect a static site and deploy it.

4) Or deploy with Vercel CLI:

```bash
npm i -g vercel
cd "D:/avishkarana_andhra_assignments/bank_fraud_detection"
vercel login
vercel --prod
```

Helper scripts are available in `scripts/` for GitHub pushes.
