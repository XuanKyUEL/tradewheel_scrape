# 🔧 N8N Webhook Setup Guide

## 📋 Bước 1: Import Workflow

1. **Mở n8n** (https://n8n-qviom-u47294.vm.elestio.app/)
2. **Click "+" → Import from File**
3. **Chọn file**: `n8n-tradewheel-workflow.json` 
4. **Click Import**

## ⚡ Bước 2: Activate Webhook (QUAN TRỌNG!)

1. **Mở workflow vừa import**
2. **Click nút "Execute Workflow"** ở góc phải dưới
3. **Webhook sẽ được activate** và hiển thị status "Waiting for webhook call..."
4. **Copy Production URL** từ webhook node

## 🔗 Bước 3: Configure GitHub Secret

1. **Vào GitHub repo**: https://github.com/XuanKyUEL/tradewheel_scrape
2. **Settings → Secrets and variables → Actions**
3. **New repository secret**:
   - Name: `N8N_WEBHOOK_URL`
   - Value: `https://n8n-qviom-u47294.vm.elestio.app/webhook/tradewheel-scrape-completed`

## 🎯 Bước 4: Test Webhook

### Manual Test từ Terminal:
```powershell
curl -X POST "https://n8n-qviom-u47294.vm.elestio.app/webhook/tradewheel-scrape-completed" `
     -H "Content-Type: application/json" `
     -d '{"status":"success","file_name":"test.xlsx","scrape_date":"2025-08-15","github_view_url":"https://github.com/test","download_url":"https://github.com/test/raw"}'
```

## 🔄 Bước 5: Set Workflow to Always Active

1. **Trong n8n workflow**
2. **Click Settings (⚙️) ở góc phải**
3. **Bật "Active"** để workflow luôn chạy
4. **Save**

## ⚠️ Lưu ý quan trọng:

- **Webhook URL đúng**: `/webhook/tradewheel-scrape-completed` (Production URL)
- **Always Active**: Phải bật để webhook hoạt động 24/7
- **Authentication**: Không cần, webhook này public access
- **Test vs Production**: Dùng Production URL cho GitHub Actions

## 🐛 Troubleshooting:

- **404 Error**: Workflow chưa active hoặc sai URL
- **Authentication Error**: Kiểm tra Zalo credentials trong n8n
- **No response**: Kiểm tra GitHub Actions logs
