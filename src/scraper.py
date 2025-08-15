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
            self.driver.set_page_load_timeout(self.config['scraping']["page_load_timeout"])
            print("✅ WebDriver đã sẵn sàng")
            return True
        except Exception as e:
            print(f"❌ Lỗi thiết lập WebDriver: {e}")
            return False
    
    def scrape_page(self, page_num):
        """Scrape dữ liệu từ một trang"""
        current_url = f"{self.config['scraping']['base_url']}?page={page_num}"
        print(f"📄 Đang scrape trang {page_num} - {current_url}")
        
        try:
            self.driver.get(current_url)
            time.sleep(3)  # Chờ trang load
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            lead_containers = soup.find_all("div", class_="bo-list-left")
            
            if not lead_containers:
                print(f"⚠️ Trang {page_num} không có dữ liệu")
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
                print(f"📊 Tổng leads: {total_leads}")
                return True, excel_file, total_leads
            else:
                print(f"⚠️ Giữ lại file CSV: {csv_file}")
                return False, csv_file, total_leads
                
        except Exception as e:
            print(f"❌ Lỗi trong quá trình scraping: {e}")
            return False, None, 0
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 WebDriver đã đóng")
