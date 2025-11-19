# Example: URL-Based Deduplication in Action

This document shows a practical example of how the URL-based deduplication feature works.

## Scenario

You have already scraped Tradewheel data several times, and your `data/` directory contains:

```
data/
├── 08_15_25_tradewheel_scrap.csv  (199 leads)
├── 09_01_25_tradewheel_scrap.csv  (198 leads)
├── 09_03_25_tradewheel_scrap.csv  (199 leads)
├── 09_15_25_tradewheel_scrap.csv  (199 leads)
├── 09_16_25_tradewheel_scrap.csv  (199 leads)
├── 09_17_25_tradewheel_scrap.csv  (196 leads)
├── 09_29_25_tradewheel_scrap.csv  (199 leads)
├── 10_20_25_tradewheel_scrap.csv  (20 leads)
├── 10_29_25_tradewheel_scrap.csv  (199 leads)
├── 11_01_25_tradewheel_scrap.csv  (198 leads)
└── 11_15_25_tradewheel_scrap.csv  (20 leads)

Total: 1,722 unique URLs
```

## Running a New Scrape

When you run the scraper on November 19, 2025:

```bash
python src/main.py
```

### Step 1: Scraping Pages
```
🚀 Bắt đầu scrape từ trang 1 đến 15
📄 Đang scrape trang 1 - https://www.tradewheel.com/buyers/?page=1
✅ Tìm thấy 20 leads mới
📄 Đang scrape trang 2 - https://www.tradewheel.com/buyers/?page=2
✅ Tìm thấy 20 leads mới
...
📄 Đang scrape trang 15 - https://www.tradewheel.com/buyers/?page=15
✅ Tìm thấy 20 leads mới
📊 Tổng cộng: 300 leads từ 300 records
```

### Step 2: Loading Previous URLs
```
📂 Found 11 previous CSV files
✅ Loaded 1722 unique URLs from previous data
```

The scraper reads all 11 CSV files and builds a set of 1,722 unique URLs that have been scraped before.

### Step 3: Deduplication
```
🔍 Deduplication: 300 → 145 (155 duplicates removed)
```

Out of the 300 newly scraped leads:
- **155 URLs** already exist in previous files → **Removed**
- **145 URLs** are new and unique → **Kept**

### Step 4: Saving Results
```
💾 Đang lưu CSV: data/11_19_25_tradewheel_scrap.csv
✅ Đã lưu 145 records vào CSV
🔄 Đang convert sang Excel: data/11_19_25_tradewheel_scrap.xlsx
✅ Đã convert thành công sang Excel

🎉 HOÀN THÀNH!
📁 File Excel: data/11_19_25_tradewheel_scrap.xlsx
📊 Unique leads saved: 145
```

## Result

Your `data/` directory now contains:

```
data/
├── ... (previous files)
├── 11_15_25_tradewheel_scrap.csv  (20 leads)
└── 11_19_25_tradewheel_scrap.csv  (145 leads) ← NEW FILE with only unique data!

Total: 1,867 unique URLs (1,722 + 145)
```

## Benefits Demonstrated

1. **Space Savings**: Saved 51.7% storage by not storing 155 duplicate entries
2. **Data Quality**: Maintained clean dataset with no duplicates
3. **Efficiency**: Only new data is saved
4. **Automatic**: No manual intervention needed

## What Gets Deduplicated?

### Example Duplicate (Removed)
```csv
"USA","14 Nov, 2025","Looking for Lentils","https://www.tradewheel.com/buyers/looking-for-lentils/900673/","Hello, I need Lentils","2025-11-19 10:00:00"
```
This URL already exists in `11_15_25_tradewheel_scrap.csv`, so it's **removed**.

### Example New Entry (Kept)
```csv
"Germany","19 Nov, 2025","Importing Steel Pipes","https://www.tradewheel.com/buyers/importing-steel-pipes/900800/","Need steel pipes for construction","2025-11-19 10:00:00"
```
This URL is new and doesn't exist in any previous file, so it's **kept**.

## Edge Cases Handled

### Case 1: First Run (No Previous Data)
```
ℹ️ No previous CSV files found
🔍 Deduplication: 300 → 300 (0 duplicates removed)
```
All 300 leads are saved because this is the first scraping run.

### Case 2: All Duplicates
```
📂 Found 11 previous CSV files
✅ Loaded 1722 unique URLs from previous data
🔍 Deduplication: 300 → 0 (300 duplicates removed)
❌ Không có dữ liệu mới sau khi loại bỏ duplicate!
```
No new file is created because all scraped data already exists.

### Case 3: Intra-Batch Duplicates
```
📄 Đang scrape trang 1 - (finds URL A)
📄 Đang scrape trang 2 - (finds URL A again)
```
The duplicate within the same batch is also removed, ensuring each URL appears only once.

## Verification

You can verify the deduplication is working:

```bash
# Run the verification script
python verify_deduplication.py

# Check unique URLs in all files
find data/*.csv -exec wc -l {} \; | awk '{sum+=$1} END {print sum}'
```

## Summary

The deduplication feature ensures that:
- ✅ Every URL is stored only once across all CSV files
- ✅ Storage is optimized by not saving duplicates
- ✅ Data quality is maintained automatically
- ✅ Git commits only contain new, unique data
