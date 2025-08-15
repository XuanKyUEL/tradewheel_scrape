#!/usr/bin/env python3
"""
Quick test script để verify setup
Chạy 1-2 trang để test cấu hình
"""

import sys
import os
sys.path.append('src')

def test_imports():
    """Test import các modules"""
    try:
        from scraper import TradewheelScraper
        print("✅ Import scraper module: OK")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test config loading"""
    try:
        from scraper import TradewheelScraper
        scraper = TradewheelScraper()
        print("✅ Config loading: OK")
        print(f"📄 Default pages: {scraper.config['scraping']['start_page']}-{scraper.config['scraping']['end_page']}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_minimal_scrape():
    """Test minimal scraping (1 page only)"""
    try:
        from scraper import TradewheelScraper
        print("🧪 Testing minimal scrape (1 page)...")
        
        scraper = TradewheelScraper()
        success, output_file, total_leads = scraper.run(start_page=1, end_page=1)
        
        if success:
            print(f"✅ Minimal scrape: SUCCESS")
            print(f"📄 Output: {output_file}")
            print(f"📊 Leads: {total_leads}")
            return True
        else:
            print(f"❌ Minimal scrape: FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Scrape error: {e}")
        return False

def main():
    """Main test function"""
    print("="*50)
    print("🧪 TRADEWHEEL SCRAPER SETUP TEST")
    print("="*50)
    
    tests = [
        ("Import Test", test_imports),
        ("Config Test", test_config),
        ("Minimal Scrape Test", test_minimal_scrape)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"⚠️ {test_name} failed!")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Setup is ready.")
        print("\n📋 Next steps:")
        print("1. Push to GitHub repository")
        print("2. Enable GitHub Actions")
        print("3. Test manual workflow run")
    else:
        print("❌ Some tests failed. Check configuration.")

if __name__ == "__main__":
    main()
