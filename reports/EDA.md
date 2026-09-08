# BÁO CÁO TÓM TẮT KIỂM TRA DỮ LIỆU VÀ KHÁM PHÁ EDA

**Dự án:** Store-Level Sales Forecasting Engine (Walmart)  
**File dữ liệu:** `train_final.csv`  
**Đơn vị phân tích:** Cấp Cửa hàng - Tuần (Store - Date Level)

---

## 1. TỔNG QUAN & KIỂM TRA SỨC KHỎE DỮ LIỆU (HEALTH CHECK)

* **Quy mô tập dữ liệu:** 2,925 dòng x 22 cột (45 Cửa hàng x 65 tuần dữ liệu liên tục).
* **Khung thời gian:** Từ `2011-02-04` đến `2012-04-27` (Chuỗi thời gian đồng nhất 100%).
* **Số dòng trùng lặp:** 0 dòng (0%).
* **Độ sạch đặc trưng cốt lõi:** 100% các cột `Weekly_Sales`, `Lag_1`, `Lag_52`, `Rolling_Mean_4w`, `Size`, `CPI`, `Unemployment`, `Temperature`, `Fuel_Price` không bị khuyết thiếu (0% Missing).
* **Xử lý biến MarkDown:** Tỷ lệ khuyết ~61% - 67% (do Walmart chỉ thu thập từ tháng 11/2011). Model có thể chuẩn hóa bằng cách điền giá trị `0`.

---

## 2. THỐNG KÊ MÔ TẢ (DESCRIPTIVE STATISTICS)

| Tên biến | Trung bình (Mean) | Trung vị (Median) | Min | Max | Độ lệch (Skew) | Nhận định QC |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Weekly_Sales** | $1,048,165.69 | $951,569.84 | $215,359.21 | $3,676,388.98 | 0.67 | Lệch phải nhẹ do đợt bùng nổ Tết. |
| **Lag_1** | $1,046,758.19 | $951,244.66 | $215,359.21 | $3,676,388.98 | 0.67 | Khớp phân bố 1:1 với Doanh số gốc. |
| **Lag_52** | $1,040,958.76 | $957,997.52 | $209,986.25 | $3,818,686.45 | 0.73 | Giữ nguyên phân bố mùa vụ 1 năm trước. |
| **Rolling_Mean_4w** | $1,043,690.55 | $955,580.04 | $240,433.98 | $2,790,772.07 | 0.54 | Triệt tiêu bớt nhiễu ngắn hạn. |
| **Size** | 130,287 sq ft | 126,512 sq ft | 34,875 sq ft | 219,622 sq ft | -0.19 | Phân bố diện tích khá đồng đều. |
| **Unemployment** | 7.91% | 7.77% | 4.12% | 14.02% | 1.21 | Có sự phân hóa rõ giữa các vùng. |

* **Kiểm tra logic kinh doanh:** 0 dòng có doanh số âm hoặc bằng $0; 0 dòng bị dị biệt âm ở biến trễ.

---

## 3. PHÂN TÍCH CHUỖI THỜI GIAN & MÙA VỤ (TIME-SERIES & SEASONALITY INSIGHTS)

* **Tác động Ngày lễ (IsHoliday):**
  * Doanh số trung bình tuần Ngày lễ đạt **$1,141,088** (tăng **9.7%** so với tuần thường **$1,040,422**).
  * Trung vị doanh số tuần lễ đạt **$1,034,448** (tăng **9.35%** so với tuần thường **$945,975**).
* **Xu hướng Mùa vụ theo Tháng:**
  * **Đỉnh cao điểm:** Tháng 11 và Tháng 12 vọt lên mốc **$1.2M - $1.3M/tuần** (sức mua lớn nhất năm dịp Thanksgiving, Black Friday, Christmas).
  * **Đáy thấp điểm:** Tháng 1 chạm mức thấp nhất năm (~ **$940k/tuần**) do tâm lý thắt chặt chi tiêu sau lễ.
* **Phân hóa theo Phân loại Cửa hàng (Store Type):**
  * **Type A:** Áp đảo hoàn toàn với doanh số trung vị ~ **$1.4M/tuần**.
  * **Type B:** Đạt mức trung bình ~ **$750k/tuần** (bằng 1/2 Type A).
  * **Type C:** Quy mô nhỏ nhất, trung bình ~ **$500k/tuần** (bằng 1/3 Type A).
* **Khoảng cách Top 5 vs Bottom 5 Store:**
  * Nhóm dẫn đầu (Store 4, 20, 14, 13, 10) đạt mức doanh thu trung bình **$1.9M - $2.1M/tuần**.
  * Nhóm thấp nhất (Store 38, 36, 5, 44, 33) chỉ đạt **$300k - $400k/tuần** (chênh lệch 6-7 lần).

---

## 4. MA TRẬN TƯƠNG QUAN & ĐỊNH HƯỚNG DỰ BÁO (CORRELATION ANALYSIS)

| Biến đặc trưng (Feature) | Hệ số Tương quan ($r$) | Đánh giá mức độ ảnh hưởng | Chiến lược sử dụng cho Mô hình |
| :--- | :---: | :--- | :--- |
| **Lag_52** | **0.986** | Tương quan thuận siêu mạnh | Đặc trưng trụ cột 1 (Mùa vụ 1 năm). |
| **Rolling_Mean_4w** | **0.961** | Tương quan thuận siêu mạnh | Đặc trưng trụ cột 2 (Xu hướng 4 tuần). |
| **Lag_1** | **0.953** | Tương quan thuận siêu mạnh | Đặc trưng trụ cột 3 (Đà ngắn hạn). |
| **Size** | **0.814** | Tương quan thuận rất mạnh | Xác định mức doanh số nền (Baseline). |
| **Unemployment** | -0.127 | Tương quan nghịch nhẹ | Bối cảnh kinh tế vĩ mô. |
| **CPI** | -0.065 | Tương quan nghịch nhẹ | Bối cảnh lạm phát. |
| **Temperature** | -0.064 | Tương quan nghịch nhẹ | Bối cảnh thời tiết mùa. |
| **IsHoliday** | 0.047 | Tương quan tuyến tính thấp | Mô hình cây (XGBoost) tách nhánh phi tuyến `If IsHoliday == 1`. |

---

## 5. KHUYẾN NGHỊ CHO BƯỚC MODELING (PIPELINE & MODEL GUIDELINES)

1. **Ma trận Feature:** Giữ nguyên toàn bộ 13 biến đặc trưng đã tạo (`Lag_1`, `Lag_52`, `Rolling_Mean_4w`, `Size`, `Type_encoded`, `IsHoliday`, `CPI`, `Fuel_Price`, `Unemployment`, `Temperature`, `Month`, `WeekOfYear`, `Store`). Chuẩn hóa bằng cách điền giá trị `0`cho các giá trị rỗng của các biến Markdown
2. **Loại mô hình đề xuất:** Ưu tiên **XGBoost Regressor** và **Random Forest Regressor** vì khả năng xử lý tốt quan hệ phi tuyến của biến `IsHoliday` và tự động đánh giá tầm quan trọng đặc trưng (Feature Importance).
3. **Mốc cắt Validation:** Sử dụng mốc thời gian `2012-05-01` để chia tập `train_final` (huấn luyện) và `val_set` (đánh giá sai số RMSE/MAE phục vụ Báo cáo Master).