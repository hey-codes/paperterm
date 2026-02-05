# GitHub Setup Guide

How to set up GitHub authentication for Claude Code and deploy the dashboard.

## Prerequisites

1. GitHub account
2. Git installed locally
3. Claude Code CLI

## Step 1: Install GitHub CLI

```bash
# macOS (Homebrew)
brew install gh

# Or download from: https://cli.github.com/
```

## Step 2: Authenticate GitHub CLI

Run this command and follow the prompts:

```bash
gh auth login
```

**Options to select:**
1. **Account**: GitHub.com
2. **Protocol**: HTTPS (recommended)
3. **Authenticate**: Login with a web browser
4. **Copy the code** shown in terminal
5. **Press Enter** to open browser
6. **Paste the code** in the browser
7. **Authorize** GitHub CLI

### Verify Authentication
```bash
gh auth status
```

Should show: `✓ Logged in to github.com as YOUR_USERNAME`

## Step 3: Configure Git

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 4: Create the Repository

### Option A: Create via CLI
```bash
cd /path/to/kindle-dashboard
git init
gh repo create YOUR_REPO_NAME --public --source=. --push
```

### Option B: Create via GitHub Web
1. Go to https://github.com/new
2. Name: `kindle-dashboard` (or chosen name)
3. Public repository
4. Don't initialize with README (we have files)
5. Create repository
6. Follow the "push existing repository" instructions

## Step 5: Enable GitHub Pages

1. Go to repository **Settings**
2. Click **Pages** in sidebar
3. Source: **GitHub Actions**
4. Save

## Step 6: Enable Workflow Permissions

1. Go to repository **Settings**
2. Click **Actions** → **General**
3. Scroll to "Workflow permissions"
4. Select **Read and write permissions**
5. Check **Allow GitHub Actions to create and approve pull requests**
6. Save

## Step 7: Trigger First Build

Either:
- Push a commit to main branch
- Go to Actions tab → Select workflow → Run workflow

## Step 8: Get Your Dashboard URL

After first successful deployment:
```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME/dashboard.png
```

## Step 9: Update Kindle

Configure the Kindle's TRMNL script to fetch from your URL.

---

## Troubleshooting

### "Permission denied" errors
```bash
gh auth refresh -s repo,workflow
```

### Workflow not running
- Check Actions are enabled in repo settings
- Verify workflow file is in `.github/workflows/`

### Pages not deploying
- Ensure "GitHub Actions" is selected as source
- Check workflow logs for errors

### Image not updating
- GitHub Pages has ~10 minute cache
- Add cache-busting: `?t=timestamp` to URL

---

## Claude Code Integration

Once `gh` is authenticated, Claude Code can:
- Create repositories
- Push commits
- Create pull requests
- Manage issues
- Trigger workflows

**Test it:**
```bash
gh repo list --limit 5
```
