# 🕷️ Tradewheel Auto Scraper

**Automated scraping solution for Tradewheel.com with GitHub Actions scheduling**

## 🎯 Features

- ✅ **Auto scraping every 2 weeks** via GitHub Actions
- ✅ **Automatic Excel export** with formatting
- ✅ **Data stored in repository** with version control
- ✅ **Anti-detection measures** (random delays, proper headers)
- ✅ **URL-based deduplication** - automatically removes duplicates from previous scrapes
- ✅ **Duplicate removal** and data cleaning
- ✅ **Manual triggering** support
- ✅ **Local development** support

## 📁 Project Structure

```
tradewheel-scraper/
├── .github/
│   └── workflows/
│       └── scrape-tradewheel.yml    # GitHub Actions workflow
├── src/
│   ├── main.py                      # Entry point for GitHub Actions
│   ├── scraper.py                   # Main scraper module
│   ├── config_github.py             # Production config
│   └── __init__.py                  # Package init
├── scripts/
│   └── run_local.py                 # Local development script
├── data/                            # Auto-generated data files
│   ├── MM_DD_YY_tradewheel_scrap.xlsx
│   └── MM_DD_YY_tradewheel_scrap.csv
├── config.py                        # Local config (gitignored)
├── requirements.txt                 # Python dependencies
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

## 🚀 Setup & Usage

### 1. GitHub Repository Setup

1. **Fork/Clone this repository**
2. **Enable GitHub Actions** in repository settings
3. **Repository will auto-scrape every 2 weeks**

### 2. Manual Triggering

Go to **Actions** tab → **Tradewheel Auto Scraper** → **Run workflow**

Options:

- `start_page`: Starting page (default: 1)
- `end_page`: Ending page (default: 15)

### 3. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run local test (5 pages)
python scripts/run_local.py

# Run with custom config
python src/main.py
```

### 4. Schedule Configuration

Edit `.github/workflows/scrape-tradewheel.yml`:

```yaml
schedule:
  # Every 2 weeks on Monday at 9:00 AM UTC
  - cron: "0 9 */14 * 1"

  # Other examples:
  # - cron: '0 9 * * 1'      # Every Monday
  # - cron: '0 9 */7 * *'    # Every week
  # - cron: '0 9 1 * *'      # Monthly on 1st
```

## 📊 Data Output

### Auto-generated files in `/data/`:

- `MM_DD_YY_tradewheel_scrap.xlsx` - Formatted Excel file
- `MM_DD_YY_tradewheel_scrap.csv` - Raw CSV data

### Data Structure:

| Column      | Description              |
| ----------- | ------------------------ |
| country     | Buyer's country          |
| date_posted | When the lead was posted |
| title       | Lead title/heading       |
| url         | Direct URL to the lead   |
| bdesc       | Cleaned description      |
| crawl_time  | When data was scraped    |

### Deduplication:

The scraper **automatically removes duplicates** based on the URL column:

- 🔍 Scans all previous CSV files in `/data/` directory
- 🗑️ Removes entries with URLs that already exist
- ✨ Saves only new, unique leads in each run
- 📊 Reports deduplication statistics

For more details, see [DEDUPLICATION.md](DEDUPLICATION.md)

## ⚙️ Configuration

### GitHub Actions Config (`src/config_github.py`):

```python
SCRAPING_CONFIG = {
    "start_page": 1,
    "end_page": 15,          # Adjust pages here
    "min_delay": 3,          # Delay between pages
    "max_delay": 7,
}
```

### Local Config (`config.py`):

Create `config.py` for local development:

```python
CHROME_CONFIG = {
    "binary_location": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "chromedriver_path": r"C:\path\to\chromedriver.exe",
}
```

## 🤖 GitHub Actions Workflow

The automation includes:

1. **Scheduled runs** every 2 weeks
2. **Chrome/ChromeDriver installation** on Ubuntu
3. **Data scraping** with error handling
4. **Auto-commit** results to repository
5. **Artifact upload** for backup

## 🔧 Customization

### Change Schedule:

Edit the cron expression in workflow file:

```yaml
# Every 2 weeks (current)
- cron: "0 9 */14 * 1"

# Weekly
- cron: "0 9 * * 1"

# Monthly
- cron: "0 9 1 * *"
```

### Change Page Range:

1. **For automation**: Edit `config_github.py`
2. **For manual runs**: Use workflow inputs
3. **For local**: Edit `run_local.py`

### Data Storage:

Files are automatically committed to `/data/` folder with:

- Timestamp in filename
- Git version control
- 90-day artifact retention

## 🚨 Monitoring

### Check automation status:

1. Go to **Actions** tab
2. View workflow run history
3. Check logs for errors
4. Download artifacts if needed

### Troubleshooting:

- **Workflow fails**: Check Actions logs
- **No data**: Website might be down/changed
- **Local issues**: Check Chrome/ChromeDriver paths

## 📈 Data History

All scraped data is preserved in the repository with:

- ✅ Git commit history
- ✅ Timestamped files
- ✅ Full audit trail
- ✅ Easy data comparison

## 🔒 Security

- No sensitive data stored
- Public repository safe
- Uses GitHub's secure runners
- No API keys required

---

**🎉 Set up once, data flows automatically every 2 weeks!**

- ✅ Configurable parameters
- ✅ Error handling

## Troubleshooting

### Lỗi Chrome binary

Nếu gặp lỗi Chrome binary, hãy kiểm tra đường dẫn trong `config.py`:

```python
"binary_location": r"C:\Program Files\Google\Chrome\Application\chrome.exe"
```

### Lỗi chromedriver

Kiểm tra đường dẫn chromedriver trong `config.py`:

```python
"chromedriver_path": r"E:\advantage_scrapping\chromedriver-win64\chromedriver.exe"
```
