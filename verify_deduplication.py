#!/usr/bin/env python3
"""
Verification script to demonstrate deduplication with actual repository data
"""

import sys
import csv
from pathlib import Path

sys.path.append('src')

def verify_with_actual_data():
    """Verify deduplication with actual data files"""
    print("="*60)
    print("🔍 VERIFYING DEDUPLICATION WITH ACTUAL DATA")
    print("="*60)
    
    data_dir = Path('data')
    
    if not data_dir.exists():
        print("❌ Data directory not found")
        return False
    
    csv_files = sorted(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("❌ No CSV files found in data directory")
        return False
    
    print(f"\n📂 Found {len(csv_files)} CSV files in data directory")
    
    # Load all URLs from existing files
    all_urls = set()
    file_url_counts = {}
    
    for csv_file in csv_files:
        try:
            urls_in_file = set()
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'url' in row and row['url']:
                        urls_in_file.add(row['url'])
            
            file_url_counts[csv_file.name] = len(urls_in_file)
            all_urls.update(urls_in_file)
            
        except Exception as e:
            print(f"⚠️ Error reading {csv_file.name}: {e}")
    
    print(f"\n📊 Statistics:")
    print(f"   Total CSV files: {len(csv_files)}")
    print(f"   Total unique URLs across all files: {len(all_urls)}")
    
    print(f"\n📋 URLs per file:")
    for filename, count in sorted(file_url_counts.items()):
        print(f"   {filename}: {count} URLs")
    
    # Now test deduplication with sample data
    print(f"\n🧪 Testing deduplication function...")
    
    from scraper import TradewheelScraper
    
    # Create scraper with explicit output directory
    config = {
        'scraping': {
            "start_page": 1,
            "end_page": 1,
            "base_url": "https://www.tradewheel.com/buyers/",
            "min_delay": 2,
            "max_delay": 5,
            "page_load_timeout": 10,
        },
        'chrome': {
            "binary_location": "/usr/bin/google-chrome-stable",
            "chromedriver_path": "/usr/local/bin/chromedriver",
            "headless": True,
            "user_agent": "Mozilla/5.0"
        },
        'output': {
            "output_directory": "data",  # Use relative path from root
            "file_format": "{date}_test",
            "keep_csv": True,
            "excel_sheet_name": "Test"
        },
        'excel': {
            "auto_adjust_columns": True,
            "max_column_width": 50,
            "min_column_width": 10,
            "freeze_header_row": True
        }
    }
    
    scraper = TradewheelScraper(config=config)
    
    # Simulate some new scraped data with overlaps
    # Take first 3 URLs from existing data as duplicates
    sample_existing_urls = list(all_urls)[:3]
    
    scraper.results = [
        {
            'country': 'Test Country 1',
            'date_posted': '19 Nov, 2025',
            'title': 'Duplicate Test 1',
            'url': sample_existing_urls[0] if len(sample_existing_urls) > 0 else 'test-url-1',
            'bdesc': 'This should be removed as duplicate',
            'crawl_time': '2025-11-19 10:00:00'
        },
        {
            'country': 'Test Country 2',
            'date_posted': '19 Nov, 2025',
            'title': 'New Test 1',
            'url': 'https://www.tradewheel.com/buyers/new-test-lead-1/999999/',
            'bdesc': 'This is a new lead that should be kept',
            'crawl_time': '2025-11-19 10:00:00'
        },
        {
            'country': 'Test Country 3',
            'date_posted': '19 Nov, 2025',
            'title': 'Duplicate Test 2',
            'url': sample_existing_urls[1] if len(sample_existing_urls) > 1 else 'test-url-2',
            'bdesc': 'This should also be removed as duplicate',
            'crawl_time': '2025-11-19 10:00:00'
        },
        {
            'country': 'Test Country 4',
            'date_posted': '19 Nov, 2025',
            'title': 'New Test 2',
            'url': 'https://www.tradewheel.com/buyers/new-test-lead-2/888888/',
            'bdesc': 'This is another new lead that should be kept',
            'crawl_time': '2025-11-19 10:00:00'
        }
    ]
    
    print(f"\n📊 Before deduplication: {len(scraper.results)} records")
    print(f"   - Expected duplicates: 2")
    print(f"   - Expected to keep: 2")
    
    duplicates_removed = scraper.deduplicate_data()
    
    print(f"\n📊 After deduplication: {len(scraper.results)} records")
    print(f"   - Duplicates removed: {duplicates_removed}")
    
    if duplicates_removed == 2 and len(scraper.results) == 2:
        print(f"\n✅ Deduplication working correctly!")
        print(f"   Kept only new URLs that don't exist in previous data")
        return True
    else:
        print(f"\n⚠️ Unexpected deduplication results")
        return False

if __name__ == "__main__":
    success = verify_with_actual_data()
    sys.exit(0 if success else 1)
