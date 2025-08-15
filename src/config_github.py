# GitHub Actions Config for Tradewheel Scraper

# Cấu hình scraping cho production
SCRAPING_CONFIG = {
    "start_page": 1,
    "end_page": 15,
    "base_url": "https://www.tradewheel.com/buyers/",
    "min_delay": 3,    # Tăng delay cho production
    "max_delay": 7,    
    "page_load_timeout": 15,  # Tăng timeout cho server
}

# Cấu hình Chrome cho Linux (GitHub Actions)
CHROME_CONFIG = {
    "binary_location": "/usr/bin/google-chrome-stable",  # Chrome path trên Ubuntu
    "chromedriver_path": "/usr/local/bin/chromedriver",   # ChromeDriver path
    "headless": True,  # Luôn headless trên server
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Cấu hình file output cho GitHub
OUTPUT_CONFIG = {
    "output_directory": "../data",  # Lưu vào folder data
    "file_format": "{date}_tradewheel_scrap",
    "keep_csv": True,   # Giữ cả CSV và Excel
    "excel_sheet_name": "Tradewheel_Leads"
}

# Cấu hình Excel formatting
EXCEL_CONFIG = {
    "auto_adjust_columns": True,
    "max_column_width": 50,
    "min_column_width": 10,
    "freeze_header_row": True
}
