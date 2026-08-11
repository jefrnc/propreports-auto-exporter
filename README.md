# 🚀 PropReports Auto-Exporter

[![GitHub Action](https://img.shields.io/badge/GitHub-Action-blue?logo=github)](https://github.com/marketplace/actions/propreports-auto-exporter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/github/v/release/jefrnc/propreports-auto-exporter)](https://github.com/jefrnc/propreports-auto-exporter/releases)

> Automatically export your trading data from PropReports with daily snapshots, weekly summaries, and monthly analytics.

[Español](./docs/README_ES.md) | [Installation](#-quick-start) | [Examples](./examples) | [FAQ](./docs/FAQ.md)

<!-- STATS_START -->
### 📊 Live Trading Statistics

| Period | Trades | P&L | Win Rate |
|--------|--------|-----|----------|
| **Week 30 (partial)** | 49 | **+$138.45** | 71.4% |
| Week 29 | 0 | $0.00 | 0% |
| **July (partial)** | 213 | **+$437.94** | 74.6% |
| June | 127 | **-$57.69** | 62.2% |

#### 📈 Yearly Projection

| Metric | Actual YTD | Projected EOY |
|--------|------------|---------------|
| **Trades** | 391 | 677 |
| **P&L** | **+$390.25** | **+$676.00** |

*Based on current performance with 158 days remaining*

*Last updated: 2025-07-26 23:45 UTC*
<!-- STATS_END -->

<!-- CALENDAR_START -->
## 📅 2025 Trading Calendar

![Trading Calendar](.github/assets/calendar-2025.svg)

### Legend
🟩 Profit Day | 🟨 Break Even | 🟥 Loss Day | ⬜ No Trades

### 📊 2025 Statistics

| Metric | Value |
|--------|-------|
| **Total Trading Days** | 26 |
| **Total Trades** | 391 |
| **Total P&L** | $390.25 |
| **Win Rate** | 65.4% |
| **Profit Days** | 17 (65.4%) |
| **Loss Days** | 9 (34.6%) |
| **Best Day** | $83.00 (2025-06-26) |
| **Worst Day** | $-14.00 (2025-06-13) |
| **Daily Average** | $15.01 |

### 📈 Monthly Breakdown

| Month | Trades | P&L | Win Rate |
|-------|--------|-----|----------|
| May | 51 | **+$9.70** | 70.6% |
| June | 127 | **-$57.69** | 62.2% |
| July | 213 | **+$437.94** | 74.2% |
<!-- CALENDAR_END -->

## ✨ Features

- 📅 **Daily Automatic Export** - Never miss a trade
- 📊 **Weekly Summaries** - Pattern analysis and performance metrics
- 📈 **Monthly Reports** - Deep analytics with recommendations
- 🔄 **Auto-Versioning** - Git history of all your trades
- 🔒 **Secure** - Credentials stored as GitHub Secrets
- 🛡️ **Privacy First** - Automatic account number obfuscation
- ♻️ **Smart Reprocessing** - Handles delayed trades (up to 24h)
- ⚡ **5-Minute Setup** - Start tracking immediately

## 🎯 Who is this for?

- Prop traders using PropReports
- Traders wanting automated performance tracking
- Anyone needing reliable trade data backup
- Quants requiring structured trade data for analysis

## 📚 Quick Start

### Prerequisites
- A GitHub account
- PropReports access credentials
- 5 minutes of your time

### Option 1: GitHub Actions (Recommended)

1. **Create a new private repository** on GitHub

2. **Add your credentials as secrets**:
   ```
   Settings → Secrets and variables → Actions → New repository secret
   ```
   - `PROPREPORTS_DOMAIN`: Your domain (e.g., `firm.propreports.com`)
   - `PROPREPORTS_USER`: Your username
   - `PROPREPORTS_PASS`: Your password

3. **Create `.github/workflows/export.yml`**:
   ```yaml
   name: Export Trading Data

   on:
     schedule:
       - cron: '0 3 * * *'  # Daily at 10 PM EST
     workflow_dispatch:       # Manual trigger

   jobs:
     export:
       runs-on: ubuntu-latest
       permissions:
         contents: write
       
       steps:
       - uses: actions/checkout@v3
       
       - uses: jefrnc/propreports-auto-exporter@v1
         with:
           propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
           propreports-user: ${{ secrets.PROPREPORTS_USER }}
           propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
   ```

That's it! 🎉 Your trades will be exported automatically every day.

### Option 2: Quick Setup Script

```bash
curl -sSL https://raw.githubusercontent.com/jefrnc/propreports-auto-exporter/main/quick-setup.sh | bash
```

## 🌟 Live Example

See the exporter running against a real account:
- 📊 Dynamic README statistics
- 📅 Interactive trading calendar
- 🌐 [Public track record](https://jose.ar/journal) — 5,600+ trades with curve and drawdown
- 📈 120 days of sample trading data

## 🗂️ Data Structure

```
exports/
├── daily/
│   ├── 2024-03-01.json     # Individual trades for each day
│   ├── 2024-03-02.json
│   └── ...
├── weekly/
│   ├── 2024-W09.json       # Weekly analytics (generated on weekends)
│   ├── 2024-W10.json
│   └── ...
└── monthly/
    ├── 2024-03.json        # Full monthly analysis
    └── 2024-03.txt         # Human-readable report
```

## ⚙️ Configuration

### Basic Configuration

```yaml
- uses: jefrnc/propreports-auto-exporter@v1
  with:
    propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
    propreports-user: ${{ secrets.PROPREPORTS_USER }}
    propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
```

### Advanced Configuration

```yaml
- uses: jefrnc/propreports-auto-exporter@v1
  with:
    # Required
    propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
    propreports-user: ${{ secrets.PROPREPORTS_USER }}
    propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
    
    # Optional
    export-path: 'trading-data'      # Custom export directory
    reprocess-days: '3'              # Reprocess last N days
    obfuscate-account: 'true'        # Privacy mode (default: true)
    generate-weekly: 'true'          # Force weekly summary
    generate-monthly: 'true'         # Force monthly summary
    commit-exports: 'true'           # Auto-commit (default: true)
    full-reprocess: 'false'          # Generate all summaries when reprocessing
```

### Input Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `propreports-domain` | Your PropReports domain | ✅ | - |
| `propreports-user` | Your username | ✅ | - |
| `propreports-pass` | Your password | ✅ | - |
| `export-path` | Directory for exports | ❌ | `exports` |
| `reprocess-days` | Days to reprocess for delayed trades | ❌ | `2` |
| `obfuscate-account` | Hide account numbers | ❌ | `true` |
| `generate-weekly` | Generate weekly summary | ❌ | `auto` |
| `generate-monthly` | Generate monthly summary | ❌ | `auto` |
| `commit-exports` | Auto-commit changes | ❌ | `true` |
| `full-reprocess` | Generate all summaries when reprocessing | ❌ | `false` |

## 📊 Exported Data

### Daily Export Format
```json
{
  "exportDate": "2024-03-15 22:00:00",
  "account": "AC*****23",
  "date": "2024-03-15",
  "trades": [
    {
      "date": "2024-03-15",
      "symbol": "AAPL",
      "side": "BUY",
      "quantity": 100,
      "price": 150.25,
      "pnl": 125.50,
      "commission": 1.00
    }
  ],
  "summary": {
    "totalTrades": 15,
    "totalPnL": 450.75,
    "winRate": 0.73,
    "symbols": ["AAPL", "MSFT", "GOOGL"]
  }
}
```

### Weekly Summary Includes
- Consolidated daily performance
- Trading patterns analysis
- Best/worst trading days
- Peak trading hours
- Symbol performance breakdown

### Monthly Report Features
- Comprehensive P&L analysis
- Risk metrics (Sharpe ratio, max drawdown)
- Performance by symbol
- Trading consistency metrics
- Automated recommendations
- Profit curve visualization data

## ⚠️ Important: Trade Delay Handling

> **Trades can appear up to 24 hours late in PropReports**

The system automatically handles this by:
- Reprocessing the last 2-3 days on each run
- Updating existing files with new trades
- Tracking when each file was last processed
- Configurable via `reprocess-days` parameter

## 🔧 Local Usage

### Installation
```bash
git clone https://github.com/jefrnc/propreports-auto-exporter.git
cd propreports-auto-exporter
pip install -r requirements.txt
```

### Configuration
```bash
export PROPREPORTS_DOMAIN="firm.propreports.com"
export PROPREPORTS_USER="your-username"
export PROPREPORTS_PASS="your-password"
```

### Usage
```bash
# Daily export
python src/daily_exporter.py

# Reprocess last 7 days
python src/advanced_exporter.py reprocess 7

# Export specific date range
python src/advanced_exporter.py range 2024-03-01 2024-03-15

# Generate weekly summary
python src/weekly_summary.py

# Generate monthly report
python src/monthly_summary.py

# Full reprocess with all summaries (60 days)
python src/full_reprocess.py 60
```

## 📖 Examples

### Multiple Accounts
```yaml
# Create separate workflows for each account
name: Export Account 1
# ... workflow configuration with ACCOUNT1 secrets

---
name: Export Account 2  
# ... workflow configuration with ACCOUNT2 secrets
```

### Custom Schedule
```yaml
on:
  schedule:
    # Every 4 hours during market days
    - cron: '0 */4 * * 1-5'
    # Once on weekends
    - cron: '0 22 * * 0,6'
```

### Export Without Commits
```yaml
- uses: jefrnc/propreports-auto-exporter@v1
  with:
    propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
    propreports-user: ${{ secrets.PROPREPORTS_USER }}
    propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
    commit-exports: 'false'
    
- name: Upload to S3
  # ... custom upload logic
```

### Full Historical Reprocess
```yaml
# Reprocess 60 days with all weekly/monthly summaries
- uses: jefrnc/propreports-auto-exporter@v1
  with:
    propreports-domain: ${{ secrets.PROPREPORTS_DOMAIN }}
    propreports-user: ${{ secrets.PROPREPORTS_USER }}
    propreports-pass: ${{ secrets.PROPREPORTS_PASS }}
    reprocess-days: '60'
    full-reprocess: 'true'  # Generates all summaries automatically
```

## 🛡️ Security Best Practices

1. **Always use GitHub Secrets** - Never hardcode credentials
2. **Use private repositories** - Keep your trading data secure
3. **Enable 2FA** - On both GitHub and PropReports
4. **Review permissions** - Only grant necessary access
5. **Monitor access logs** - Check for unauthorized usage

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

## 🙏 Acknowledgments

- PropReports for their platform
- The trading community for feedback and suggestions
- GitHub Actions for reliable automation

## 📞 Support

- 📧 [Open an Issue](https://github.com/jefrnc/propreports-auto-exporter/issues)
- 📚 [Read the FAQ](./docs/FAQ.md)
- 💬 [Issues](https://github.com/jefrnc/propreports-auto-exporter/issues)

---

⭐ If this project helps you, please star it!

Made with ❤️ by traders, for traders.

---

## Support this project

Free, and maintained on my own time. Sponsorship covers the market data and broker API access
behind these tools, and keeps them working when brokers change their export formats.

[![Sponsor](https://img.shields.io/badge/Sponsor-jefrnc-EA4AAA?logo=githubsponsors&logoColor=white)](https://github.com/sponsors/jefrnc)
