#!/bin/bash
# Quick setup script for PropReports Export Action

echo "🚀 PropReports Export - Quick Setup"
echo "==================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get GitHub username
echo -e "\n${BLUE}1. GitHub Configuration${NC}"
read -p "Enter your GitHub username: " github_user

# Get PropReports credentials
echo -e "\n${BLUE}2. PropReports Configuration${NC}"
read -p "Enter your PropReports domain (e.g., zim.propreports.com): " domain
read -p "Enter your PropReports username: " username
read -s -p "Enter your PropReports password: " password
echo

# Create workflow directory
echo -e "\n${YELLOW}Creating workflow directory...${NC}"
mkdir -p .github/workflows

# Create workflow file
echo -e "${YELLOW}Creating workflow file...${NC}"
cat > .github/workflows/propreports-export.yml << EOF
name: Export PropReports Data

on:
  schedule:
    # Run daily at 10 PM EST (3 AM UTC)
    - cron: '0 3 * * *'
  workflow_dispatch: # Allow manual runs

jobs:
  export-trades:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
    
    - name: Run PropReports Export
      uses: ${github_user}/propreports-exporter@v1
      with:
        propreports-domain: \${{ secrets.PROPREPORTS_DOMAIN }}
        propreports-user: \${{ secrets.PROPREPORTS_USER }}
        propreports-pass: \${{ secrets.PROPREPORTS_PASS }}
EOF

# Create initial README
echo -e "${YELLOW}Creating README...${NC}"
cat > README.md << EOF
# 📊 My PropReports Trading Data

This repository automatically exports and tracks my trading data from PropReports.

## 📈 Structure

\`\`\`
exports/
└── YYYY/
    └── MM/
        ├── daily/      # Daily trade exports
        ├── weekly/     # Weekly summaries
        └── monthly/    # Monthly analysis
\`\`\`

## 🔒 Setup

This repo uses GitHub Actions to automatically export data daily.

### Required Secrets

- \`PROPREPORTS_DOMAIN\`: $domain
- \`PROPREPORTS_USER\`: $username
- \`PROPREPORTS_PASS\`: [configured]

## 📅 Schedule

- **Daily exports**: Every day at 10 PM EST
- **Weekly summaries**: Every Sunday
- **Monthly reports**: Last day of each month

---

Powered by [PropReports Export Action](https://github.com/${github_user}/propreports-exporter)
EOF

# Create .gitignore
echo -e "${YELLOW}Creating .gitignore...${NC}"
cat > .gitignore << EOF
.env
.env.local
*.log
.DS_Store
EOF

# Instructions
echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Create a new private repository on GitHub"
echo "2. Add these secrets to your repository:"
echo "   - PROPREPORTS_DOMAIN: $domain"
echo "   - PROPREPORTS_USER: $username"
echo "   - PROPREPORTS_PASS: ****"
echo "3. Push this code to your repository:"
echo -e "${YELLOW}"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial setup for PropReports export'"
echo "   git remote add origin https://github.com/$github_user/YOUR-REPO-NAME.git"
echo "   git push -u origin main"
echo -e "${NC}"
echo "4. The action will run automatically at 10 PM EST daily!"
echo ""
echo "📚 Full documentation: https://github.com/$github_user/propreports-exporter"