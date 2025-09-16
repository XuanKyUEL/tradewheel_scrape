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
   - **Value:** `https://8f4hitdl1.tino.page/webhook/tradewheel-scrape-completed`

4. **Click "Add secret"**

## 🌐 **Lấy n8n webhook URL:**

Từ n8n workflow, webhook URL sẽ có dạng:

```
https://8f4hitdl1.tino.page/webhook/tradewheel-scrape-completed
```

## ✅ **Verify setup:**

Sau khi thêm secret, workflow sẽ có thể:

- Tự động detect file Excel đã tạo
- Gọi n8n webhook với file info
- n8n nhận data và gửi qua Zalo

---

**💡 Lưu ý:** GitHub Secrets được mã hóa và chỉ visible trong workflow runs.

---

## 📁 Webhook File Selection Logic

- Primary: Lấy file `.xlsx` được thay đổi trong commit mới nhất (`git log -1 --name-only -- data/*.xlsx`).
- Fallback: Nếu không tìm thấy từ commit, chọn file `.xlsx` mới nhất theo thời gian sửa đổi (`ls -t data/*.xlsx | head -1`).
- Mục tiêu: Đảm bảo `github_view_url` và `download_url` luôn trỏ tới file của lần chạy gần nhất, tránh chọn nhầm theo thứ tự chữ cái (ví dụ `08_*` trước `09_*`).
- Gợi ý: Mỗi lần chạy nên chỉ tạo/mở mới một file `.xlsx` (định dạng ngày `{MM_DD_YY}_tradewheel_scrap.xlsx`) để logic chọn file luôn chính xác.
