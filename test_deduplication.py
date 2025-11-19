#!/usr/bin/env python3
"""
Test script for URL-based deduplication functionality
"""

import sys
import os
import csv
from pathlib import Path

sys.path.append('src')

def create_test_data():
    """Create test CSV files with sample data"""
    test_data_dir = Path('/tmp/test_dedup_data')
    test_data_dir.mkdir(exist_ok=True)
    
    # Create first test file with some URLs
    test_file1 = test_data_dir / "test1.csv"
    with open(test_file1, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['country', 'date_posted', 'title', 'url', 'bdesc', 'crawl_time'])
        writer.writeheader()
        writer.writerows([
            {
                'country': 'USA',
                'date_posted': '01 Nov, 2025',
                'title': 'Test Lead 1',
                'url': 'https://www.tradewheel.com/buyers/test-1/123/',
                'bdesc': 'This is test lead 1',
                'crawl_time': '2025-11-01 10:00:00'
            },
            {
                'country': 'UK',
                'date_posted': '02 Nov, 2025',
                'title': 'Test Lead 2',
                'url': 'https://www.tradewheel.com/buyers/test-2/456/',
                'bdesc': 'This is test lead 2',
                'crawl_time': '2025-11-01 10:00:00'
            }
        ])
    
    # Create second test file with some overlapping URLs
    test_file2 = test_data_dir / "test2.csv"
    with open(test_file2, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['country', 'date_posted', 'title', 'url', 'bdesc', 'crawl_time'])
        writer.writeheader()
        writer.writerows([
            {
                'country': 'Germany',
                'date_posted': '03 Nov, 2025',
                'title': 'Test Lead 3',
                'url': 'https://www.tradewheel.com/buyers/test-3/789/',
                'bdesc': 'This is test lead 3',
                'crawl_time': '2025-11-03 10:00:00'
            }
        ])
    
    print(f"✅ Created test data files in {test_data_dir}")
    return test_data_dir

def test_load_previous_urls():
    """Test loading URLs from previous files"""
    print("\n🧪 Test 1: Load Previous URLs")
    print("="*50)
    
    from scraper import TradewheelScraper
    
    # Create test data
    test_dir = create_test_data()
    
    # Create scraper with custom output directory
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
            "output_directory": str(test_dir),
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
    previous_urls = scraper.load_previous_urls()
    
    print(f"📊 Loaded URLs: {previous_urls}")
    
    expected_urls = {
        'https://www.tradewheel.com/buyers/test-1/123/',
        'https://www.tradewheel.com/buyers/test-2/456/',
        'https://www.tradewheel.com/buyers/test-3/789/'
    }
    
    if previous_urls == expected_urls:
        print("✅ Test PASSED: All URLs loaded correctly")
        return True
    else:
        print(f"❌ Test FAILED: Expected {expected_urls}, got {previous_urls}")
        return False

def test_deduplicate_data():
    """Test deduplication functionality"""
    print("\n🧪 Test 2: Deduplicate Data")
    print("="*50)
    
    from scraper import TradewheelScraper
    
    # Create test data
    test_dir = create_test_data()
    
    # Create scraper with custom output directory
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
            "output_directory": str(test_dir),
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
    
    # Add some test results (some duplicates, some new)
    scraper.results = [
        {
            'country': 'USA',
            'date_posted': '01 Nov, 2025',
            'title': 'Test Lead 1',
            'url': 'https://www.tradewheel.com/buyers/test-1/123/',  # Duplicate
            'bdesc': 'This is test lead 1',
            'crawl_time': '2025-11-05 10:00:00'
        },
        {
            'country': 'France',
            'date_posted': '05 Nov, 2025',
            'title': 'Test Lead 4',
            'url': 'https://www.tradewheel.com/buyers/test-4/999/',  # New
            'bdesc': 'This is test lead 4',
            'crawl_time': '2025-11-05 10:00:00'
        },
        {
            'country': 'Germany',
            'date_posted': '03 Nov, 2025',
            'title': 'Test Lead 3',
            'url': 'https://www.tradewheel.com/buyers/test-3/789/',  # Duplicate
            'bdesc': 'This is test lead 3',
            'crawl_time': '2025-11-05 10:00:00'
        },
        {
            'country': 'Japan',
            'date_posted': '06 Nov, 2025',
            'title': 'Test Lead 5',
            'url': 'https://www.tradewheel.com/buyers/test-5/888/',  # New
            'bdesc': 'This is test lead 5',
            'crawl_time': '2025-11-05 10:00:00'
        }
    ]
    
    print(f"📊 Before deduplication: {len(scraper.results)} records")
    
    duplicates_removed = scraper.deduplicate_data()
    
    print(f"📊 After deduplication: {len(scraper.results)} records")
    print(f"🗑️ Duplicates removed: {duplicates_removed}")
    
    # Should have removed 2 duplicates, keeping 2 new ones
    if len(scraper.results) == 2 and duplicates_removed == 2:
        print("✅ Test PASSED: Deduplication worked correctly")
        
        # Verify the remaining URLs are the new ones
        remaining_urls = {item['url'] for item in scraper.results}
        expected_urls = {
            'https://www.tradewheel.com/buyers/test-4/999/',
            'https://www.tradewheel.com/buyers/test-5/888/'
        }
        
        if remaining_urls == expected_urls:
            print("✅ Remaining URLs are correct")
            return True
        else:
            print(f"❌ Wrong URLs remaining: {remaining_urls}")
            return False
    else:
        print(f"❌ Test FAILED: Expected 2 records and 2 duplicates removed")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 DEDUPLICATION FUNCTIONALITY TESTS")
    print("="*60)
    
    tests = [
        ("Load Previous URLs", test_load_previous_urls),
        ("Deduplicate Data", test_deduplicate_data)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n" + "="*60)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    print("="*60)
    
    if passed == len(tests):
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
