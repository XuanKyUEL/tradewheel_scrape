"""
Tradewheel Scraper Module
Tự động scrape dữ liệu từ Tradewheel.com và export Excel
"""

import csv
import json
import time
import re
import random
import pandas as pd
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pathlib import Path

class TradewheelScraper:
    """Class chính để scrape dữ liệu từ Tradewheel"""
    
    def __init__(self, config=None):
        self.driver = None
        self.results = []
        self.gmt7_timezone = ZoneInfo("Asia/Ho_Chi_Minh")
        self.crawl_timestamp = datetime.now(self.gmt7_timezone)
        self.config = config or self._load_default_config()
        
    def _load_default_config(self):
        """Load config mặc định"""
        try:
            # Thử import config local trước
            if os.path.exists('config.py'):
                from config import SCRAPING_CONFIG, CHROME_CONFIG, OUTPUT_CONFIG, EXCEL_CONFIG
            # Nếu không có thì dùng config GitHub
            elif os.path.exists('config_github.py'):
                from config_github import SCRAPING_CONFIG, CHROME_CONFIG, OUTPUT_CONFIG, EXCEL_CONFIG
            else:
                raise ImportError("No config found")
                
            return {
                'scraping': SCRAPING_CONFIG,
                'chrome': CHROME_CONFIG,
                'output': OUTPUT_CONFIG,
                'excel': EXCEL_CONFIG
            }
        except ImportError:
            # Fallback config
            return self._get_fallback_config()
    
    def _get_fallback_config(self):
        """Config fallback nếu không có file config"""
        return {
            'scraping': {
                "start_page": 1,
                "end_page": 10,
                "base_url": "https://www.tradewheel.com/buyers/",
                "min_delay": 2,
                "max_delay": 5,
                "page_load_timeout": 10,
            },
            'chrome': {
                "binary_location": "/usr/bin/google-chrome-stable",
                "chromedriver_path": "/usr/local/bin/chromedriver",
                "headless": True,
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            },
            'output': {
                "output_directory": "../data",
                "file_format": "{date}_tradewheel_scrap",
                "keep_csv": True,
                "excel_sheet_name": "Tradewheel_Leads"
            },
            'excel': {
                "auto_adjust_columns": True,
                "max_column_width": 50,
                "min_column_width": 10,
                "freeze_header_row": True
            }
        }
        
    def clean_description(self, text):
        """Làm sạch và chuẩn hóa text description"""
        if not isinstance(text, str): 
            return ""
        text = text.replace('\n', ' ')
        text = text.replace('•', '')
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def load_previous_urls(self):
        """Load all URLs from previous scraped data files"""
        previous_urls = set()
        
        # Xác định output directory
        if self.config['output']["output_directory"]:
            output_dir = Path(self.config['output']["output_directory"])
        else:
            output_dir = Path.cwd()
        
        # Kiểm tra nếu directory tồn tại
        if not output_dir.exists():
            print("ℹ️ No previous data directory found")
            return previous_urls
        
        # Đọc tất cả các file CSV trong directory
        csv_files = list(output_dir.glob("*.csv"))
        
        if not csv_files:
            print("ℹ️ No previous CSV files found")
            return previous_urls
        
        print(f"📂 Found {len(csv_files)} previous CSV files")
        
        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'url' in row and row['url']:
                            previous_urls.add(row['url'])
            except Exception as e:
                print(f"⚠️ Error reading {csv_file.name}: {e}")
                continue
        
        print(f"✅ Loaded {len(previous_urls)} unique URLs from previous data")
        return previous_urls
    
    def deduplicate_data(self, previous_urls=None):
        """Remove duplicate entries based on URL column"""
        if not self.results:
            print("ℹ️ No data to deduplicate")
            return 0
        
        original_count = len(self.results)
        
        # Load previous URLs if not provided
        if previous_urls is None:
            previous_urls = self.load_previous_urls()
        
        # Filter out duplicates
        deduplicated_results = []
        duplicates_found = 0
        
        for item in self.results:
            url = item.get('url', '')
            if url and url in previous_urls:
                duplicates_found += 1
            else:
                deduplicated_results.append(item)
                if url:  # Add to set to prevent intra-batch duplicates
                    previous_urls.add(url)
        
        self.results = deduplicated_results
        new_count = len(self.results)
        
        print(f"🔍 Deduplication: {original_count} → {new_count} ({duplicates_found} duplicates removed)")
        return duplicates_found
    
    def setup_driver(self):
        """Thiết lập Chrome WebDriver"""
        print("🔧 Đang thiết lập WebDriver...")
        
        options = Options()
        chrome_config = self.config['chrome']
        
        # Check if Chrome binary exists
        if os.path.exists(chrome_config["binary_location"]):
            options.binary_location = chrome_config["binary_location"]
        
        options.add_argument(f"user-agent={chrome_config['user_agent']}")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--lang=en-US,en")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_experimental_option(
            "prefs",
            {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "intl.accept_languages": "en-US,en"
            }
        )
        
        if chrome_config["headless"]:
            options.add_argument("--headless")
        
        try:
            # Try to use specified chromedriver path
            if os.path.exists(chrome_config["chromedriver_path"]):
                service = ChromeService(executable_path=chrome_config["chromedriver_path"])
            else:
                # Let Selenium auto-detect
                service = ChromeService()
                
            self.driver = webdriver.Chrome(service=service, options=options)
            self._apply_stealth_mode()
            self.driver.set_page_load_timeout(self.config['scraping']["page_load_timeout"])
            print("✅ WebDriver đã sẵn sàng")
            return True
        except Exception as e:
            print(f"❌ Lỗi thiết lập WebDriver: {e}")
            return False

    def _apply_stealth_mode(self):
        """Reduce automation fingerprints to avoid Cloudflare blocks"""
        if not self.driver:
            return
        try:
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    window.chrome = {runtime: {}};
                """
            })
        except Exception as e:
            print(f"⚠️ Không thể thiết lập stealth mode: {e}")
    
    def debug_page_content(self, page_num, soup):
        """Debug page content when no data is found"""
        print(f"\n🔍 DEBUG INFO for page {page_num}:")
        
        # Check current URL
        print(f"   Current URL: {self.driver.current_url}")
        
        # Check page title
        print(f"   Page Title: {self.driver.title}")
        
        # Check for common blocking elements
        blocking_indicators = [
            ("Cloudflare", "cf-browser-verification"),
            ("Captcha", "captcha"),
            ("Access Denied", "access-denied"),
            ("Rate Limit", "rate-limit"),
            ("Error", "error-page")
        ]
        
        for name, class_name in blocking_indicators:
            if soup.find(class_=class_name) or name.lower() in self.driver.page_source.lower():
                print(f"   ⚠️ {name} detected!")
        
        # Check for alternative container classes
        alternative_containers = [
            "bo-list-left",
            "buyer-list",
            "lead-item",
            "rbo-inner",
            "search-result"
        ]
        
        print(f"\n   Checking alternative containers:")
        for container_class in alternative_containers:
            count = len(soup.find_all("div", class_=container_class))
            if count > 0:
                print(f"   ✓ Found {count} elements with class '{container_class}'")
        
        # Save page source for debugging (first 1000 chars)
        page_snippet = self.driver.page_source[:1000]
        print(f"\n   Page source snippet:\n   {page_snippet}...")
        
        # Try to save screenshot if possible
        try:
            screenshot_path = f"/tmp/page_{page_num}_debug.png"
            self.driver.save_screenshot(screenshot_path)
            print(f"   📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"   ⚠️ Could not save screenshot: {e}")
        
        print(f"🔍 END DEBUG INFO\n")
    
    def check_and_close_popup(self):
        """Check for popup and close it if exists"""
        try:
            # Wait briefly for popup to potentially appear
            # The popup id is 'signup_modal' based on the screenshot
            # The close button is inside it
            
            # Using a short timeout because we don't want to wait long if it doesn't appear
            wait = WebDriverWait(self.driver, 5) 
            
            # Check if modal is visible
            modal = wait.until(EC.visibility_of_element_located((By.ID, "signup_modal")))
            
            if modal.is_displayed():
                print("⚠️ Popup detected, attempting to close...")
                # Find the close button within the modal
                close_button = modal.find_element(By.CSS_SELECTOR, "#signup_modal button.close")
                # Use JavaScript click to ensure it works even if obscured
                self.driver.execute_script("arguments[0].click();", close_button)
                print("✅ Popup closed")
                time.sleep(1) # Wait for animation
                
        except (TimeoutException, NoSuchElementException):
            # Popup didn't appear or couldn't be found, which is fine
            pass
        except Exception as e:
            print(f"⚠️ Error handling popup: {e}")

    def _is_cloudflare_challenge(self, page_source):
        """Detect Cloudflare challenge pages"""
        keywords = ["Just a moment", "cf-browser-verification", "__cf_chl"]
        return any(keyword in page_source for keyword in keywords)

    def wait_for_lead_containers(self, url, max_wait=25, max_retries=2):
        """Wait for lead containers to appear, retrying if Cloudflare blocks"""
        for attempt in range(max_retries + 1):
            start_time = time.time()
            while time.time() - start_time < max_wait:
                page_source = self.driver.page_source
                if self._is_cloudflare_challenge(page_source):
                    print("⚠️ Cloudflare challenge detected, waiting...")
                    time.sleep(3)
                    continue
                soup = BeautifulSoup(page_source, "html.parser")
                lead_containers = soup.find_all("div", class_="bo-list-left")
                if lead_containers:
                    return soup, lead_containers
                time.sleep(1)
            if attempt < max_retries:
                print("🔁 Không tìm thấy dữ liệu, tải lại trang để thử lại...")
                self.driver.get(url)
                time.sleep(3)
                self.check_and_close_popup()
        return BeautifulSoup(self.driver.page_source, "html.parser"), []

    def scrape_page(self, page_num):
        """Scrape dữ liệu từ một trang"""
        current_url = f"{self.config['scraping']['base_url']}?page={page_num}"
        print(f"📄 Đang scrape trang {page_num} - {current_url}")
        
        try:
            self.driver.get(current_url)
            time.sleep(3)  # Chờ trang load
            
            self.check_and_close_popup()

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            lead_containers = soup.find_all("div", class_="bo-list-left")
            
            if not lead_containers:
                print(f"⚠️ Trang {page_num} không có dữ liệu")
                self.debug_page_content(page_num, soup)
                return 0
            
            leads_found = 0
            crawl_time_str = self.crawl_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # Kiểm tra duplicate
            existing_descriptions = {item['bdesc'] for item in self.results}
            
            for lead in lead_containers:
                try:
                    # Extract description
                    desc_element = lead.find("p", class_="bdesc")
                    if not desc_element:
                        continue
                    
                    raw_desc = desc_element.get_text(strip=True)
                    cleaned_desc = self.clean_description(raw_desc)
                    
                    # Skip nếu duplicate
                    if cleaned_desc in existing_descriptions:
                        continue
                    
                    # Extract title và URL
                    a_tag = lead.select_one('h3 a, h4 a')
                    title = a_tag.get_text(strip=True) if a_tag else 'N/A'
                    url = a_tag['href'] if a_tag else 'N/A'
                    
                    # Extract date posted
                    date_container = lead.find("div", {"class": "rbo-specs", "style": "margin-top:5px;"})
                    date_posted = 'N/A'
                    if date_container:
                        date_posted = date_container.get_text(strip=True).replace("Date Posted:", "").strip()
                    
                    # Extract country
                    country_element = lead.find("div", class_="country-name-wrapper")
                    country = country_element.get_text(strip=True) if country_element else 'N/A'
                    
                    # Thêm vào kết quả
                    lead_data = {
                        "country": country,
                        "date_posted": date_posted,
                        "title": title,
                        "url": url,
                        "bdesc": cleaned_desc,
                        "crawl_time": crawl_time_str
                    }
                    
                    self.results.append(lead_data)
                    existing_descriptions.add(cleaned_desc)
                    leads_found += 1
                    
                except Exception as e:
                    print(f"⚠️ Lỗi xử lý lead: {e}")
                    continue
            
            print(f"✅ Tìm thấy {leads_found} leads mới")
            return leads_found
            
        except Exception as e:
            print(f"❌ Lỗi scrape trang {page_num}: {e}")
            return 0
    
    def scrape_all_pages(self, start_page=None, end_page=None):
        """Scrape tất cả các trang"""
        start_page = start_page or self.config['scraping']["start_page"]
        end_page = end_page or self.config['scraping']["end_page"]
        
        print(f"🚀 Bắt đầu scrape từ trang {start_page} đến {end_page}")
        
        total_leads = 0
        for page_num in range(start_page, end_page + 1):
            leads_on_page = self.scrape_page(page_num)
            total_leads += leads_on_page
            
            # Random delay giữa các trang
            if page_num < end_page:
                delay = random.uniform(
                    self.config['scraping']["min_delay"], 
                    self.config['scraping']["max_delay"]
                )
                print(f"⏱️ Nghỉ {delay:.1f} giây...")
                time.sleep(delay)
        
        print(f"📊 Tổng cộng: {total_leads} leads từ {len(self.results)} records")
        return total_leads
    
    def save_to_csv(self, filename):
        """Lưu dữ liệu ra CSV"""
        print(f"💾 Đang lưu CSV: {filename}")
        
        fieldnames = ['country', 'date_posted', 'title', 'url', 'bdesc', 'crawl_time']
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"✅ Đã lưu {len(self.results)} records vào CSV")
    
    def convert_to_excel(self, csv_file, excel_file):
        """Convert CSV sang Excel với formatting"""
        print(f"🔄 Đang convert sang Excel: {excel_file}")
        
        try:
            # Đọc CSV
            df = pd.read_csv(csv_file, encoding='utf-8-sig')
            
            # Tạo Excel với formatting
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=self.config['output']["excel_sheet_name"], index=False)
                
                # Format worksheet
                worksheet = writer.sheets[self.config['output']["excel_sheet_name"]]
                
                # Auto-adjust columns nếu enable
                if self.config['excel']["auto_adjust_columns"]:
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        
                        for cell in column:
                            try:
                                length = len(str(cell.value))
                                if length > max_length:
                                    max_length = length
                            except:
                                pass
                        
                        # Set width với giới hạn
                        width = max(
                            min(max_length + 2, self.config['excel']["max_column_width"]),
                            self.config['excel']["min_column_width"]
                        )
                        worksheet.column_dimensions[column_letter].width = width
                
                # Freeze header row nếu enable
                if self.config['excel']["freeze_header_row"]:
                    worksheet.freeze_panes = 'A2'
            
            print(f"✅ Đã convert thành công sang Excel")
            return True
            
        except Exception as e:
            print(f"❌ Lỗi convert Excel: {e}")
            return False
    
    def generate_filenames(self):
        """Tạo tên file theo định dạng"""
        date_str = self.crawl_timestamp.strftime("%m_%d_%y")
        base_name = self.config['output']["file_format"].format(date=date_str)
        
        # Xác định output directory
        if self.config['output']["output_directory"]:
            output_dir = Path(self.config['output']["output_directory"])
        else:
            output_dir = Path.cwd()
        
        output_dir.mkdir(exist_ok=True)
        
        csv_file = output_dir / f"{base_name}.csv"
        excel_file = output_dir / f"{base_name}.xlsx"
        
        return str(csv_file), str(excel_file)
    
    def run(self, start_page=None, end_page=None):
        """Chạy toàn bộ quy trình scraping"""
        print("="*60)
        print("🕷️  TRADEWHEEL ENHANCED SCRAPER V2.0")
        print("="*60)
        print(f"📅 Thời gian: {self.crawl_timestamp.strftime('%Y-%m-%d %H:%M:%S')} (GMT+7)")
        
        try:
            # Setup driver
            if not self.setup_driver():
                return False, None, 0
            
            # Scrape data
            total_leads = self.scrape_all_pages(start_page, end_page)
            
            if total_leads == 0:
                print("❌ Không thu thập được dữ liệu nào!")
                return False, None, 0
            
            # Deduplicate against previous data
            self.deduplicate_data()
            
            if len(self.results) == 0:
                print("❌ Không có dữ liệu mới sau khi loại bỏ duplicate!")
                return False, None, 0
            
            # Generate filenames
            csv_file, excel_file = self.generate_filenames()
            
            # Save CSV
            self.save_to_csv(csv_file)
            
            # Convert to Excel
            excel_success = self.convert_to_excel(csv_file, excel_file)
            
            if excel_success:
                # Xóa CSV nếu không muốn giữ
                if not self.config['output']["keep_csv"]:
                    try:
                        os.remove(csv_file)
                        print(f"🗑️ Đã xóa file CSV tạm")
                    except:
                        print(f"⚠️ Không thể xóa file CSV tạm")
                
                print(f"\n🎉 HOÀN THÀNH!")
                print(f"📁 File Excel: {excel_file}")
                print(f"📊 Unique leads saved: {len(self.results)}")
                return True, excel_file, len(self.results)
            else:
                print(f"⚠️ Giữ lại file CSV: {csv_file}")
                return False, csv_file, len(self.results)
                
        except Exception as e:
            print(f"❌ Lỗi trong quá trình scraping: {e}")
            return False, None, 0
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 WebDriver đã đóng")
