#!/usr/bin/env python3
"""
Entry point cho Tradewheel Scraper
Chạy từ GitHub Actions hoặc local
"""

import os
import sys
from scraper import TradewheelScraper

def main():
    """Hàm main cho GitHub Actions"""
    print("🚀 Starting Tradewheel Scraper...")
    
    # Lấy parameters từ environment variables (GitHub Actions)
    start_page = int(os.environ.get('START_PAGE', '1'))
    end_page = int(os.environ.get('END_PAGE', '15'))
    
    print(f"📄 Scraping pages: {start_page} to {end_page}")
    
    try:
        # Khởi tạo scraper
        scraper = TradewheelScraper()
        
        # Chạy scraping
        success, output_file, total_leads = scraper.run(
            start_page=start_page,
            end_page=end_page
        )
        
        if success:
            print(f"\n✅ Scraping thành công!")
            print(f"📄 File: {output_file}")
            print(f"📊 Total: {total_leads} leads")
            
            # Return 0 for success (GitHub Actions)
            sys.exit(0)
        else:
            print(f"\n❌ Scraping thất bại!")
            # Return 1 for failure (GitHub Actions)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
