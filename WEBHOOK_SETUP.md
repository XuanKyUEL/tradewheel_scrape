# 🔧 GitHub Secrets Setup Guide

## 📝 **Cần thiết lập GitHub Secret:**

Để workflow có thể gọi n8n webhook, bạn cần thêm webhook URL vào GitHub Secrets:

### 🔑 **Thêm N8N_WEBHOOK_URL secret:**

1. **Vào GitHub repository:**

   ```
   https://github.com/XuanKyUEL/tradewheel_scrape/settings/secrets/actions
   ```

2. **Click "New repository secret"**

3. **Nhập thông tin:**

   - **Name:** `N8N_WEBHOOK_URL`
   - **Value:** `https://your-n8n-instance.com/webhook/tradewheel-scrape-completed`

4. **Click "Add secret"**

## 🌐 **Lấy n8n webhook URL:**

Từ n8n workflow, webhook URL sẽ có dạng:

```
https://your-n8n-domain.com/webhook/tradewheel-scrape-completed
```

## ✅ **Verify setup:**

Sau khi thêm secret, workflow sẽ có thể:

- Tự động detect file Excel đã tạo
- Gọi n8n webhook với file info
- n8n nhận data và gửi qua Zalo

---

**💡 Lưu ý:** GitHub Secrets được mã hóa và chỉ visible trong workflow runs.
