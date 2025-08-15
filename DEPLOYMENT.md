# 🚀 GitHub Deployment Guide

## Step-by-Step Setup

### 1. Repository Setup

```bash
# Initialize git repository (if not already)
git init

# Add all files
git add .

# Commit initial setup
git commit -m "🎉 Initial setup: Automated Tradewheel scraper with GitHub Actions"

# Add GitHub remote (replace with your repo URL)
git remote add origin https://github.com/yourusername/tradewheel-scraper.git

# Push to GitHub
git push -u origin main
```

### 2. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Actions** → **General**
4. Ensure **"Allow all actions and reusable workflows"** is selected
5. Click **Save**

### 3. Test Manual Run

1. Go to **Actions** tab
2. Click **"Tradewheel Auto Scraper"**
3. Click **"Run workflow"**
4. Leave defaults or customize:
   - Start page: `1`
   - End page: `5` (for testing)
5. Click **"Run workflow"**

### 4. Monitor First Run

1. Watch the workflow execution in real-time
2. Check logs for any errors
3. Verify data files are created in `/data/` folder
4. Confirm files are committed to repository

### 5. Verify Automation

The workflow will now run automatically:
- **Every 2 weeks** on Monday at 9:00 AM UTC
- **Next run**: Check in Actions tab

## 📋 Customization Checklist

- [ ] Update repository name/URL in this guide
- [ ] Adjust cron schedule if needed
- [ ] Modify page range in `config_github.py`
- [ ] Test with small page range first
- [ ] Monitor first few automatic runs

## 🔧 Troubleshooting

### Common Issues:

1. **Workflow Permission Denied**
   - Check Actions are enabled in repository settings
   
2. **No Files Generated**
   - Check workflow logs for errors
   - Verify website is accessible
   
3. **ChromeDriver Issues**
   - These are auto-handled in GitHub Actions
   - For local testing, update paths in `config.py`

### GitHub Actions Logs:

Navigate to: **Repository** → **Actions** → **Workflow Run** → **Job** → **Step**

## 🎯 Success Criteria

✅ Workflow runs without errors  
✅ Excel files appear in `/data/` folder  
✅ Files are automatically committed  
✅ Next run is scheduled correctly  

---

**🎉 Once setup is complete, your scraper will run automatically every 2 weeks!**
