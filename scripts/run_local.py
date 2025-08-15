#!/usr/bin/env python3
"""
Setup script cho development
Chạy local với config thông thường
"""

import sys
import os
sys.path.append('../')
from src.scraper import TradewheelScraper

def main():
    """Chạy scraper local"""
    print("🔧 Running local scraper...")
    
    scraper = TradewheelScraper()
    
    # Override config cho local
    success, output_file, total_leads = scraper.run(
        start_page=1,   # Có thể thay đổi ở đây
        end_page=5      # Test với ít trang trước
    )
    
    if success:
        print(f"\n✅ Local scraping thành công!")
        print(f"📄 File: {output_file}")
        print(f"📊 Total: {total_leads} leads")
    else:
        print(f"\n❌ Local scraping thất bại!")

if __name__ == "__main__":
    main()
