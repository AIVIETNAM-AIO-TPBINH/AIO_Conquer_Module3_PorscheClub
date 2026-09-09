# Sales Forecasting and Demand Prediction Using LightGBM and SHAP

**AIO Conquer 2026 — Module 03 · Project 3.2**

Dự án xây dựng pipeline Machine Learning để dự báo doanh số bán hàng (Weekly Sales) cho chuỗi cửa hàng Walmart, sử dụng dữ liệu lịch sử và đặc trưng ngoại sinh, đi kèm khoảng tin cậy 95% qua Split Conformal Prediction.

## Khởi động nhanh

```bash
# 1. Kích hoạt môi trường ảo (Windows)
.\env\Scripts\Activate.ps1

# 2. Cài đặt dependencies
pip install -e ".[dev]"

# 3. Xác thực môi trường
python scripts/check_env.py

# 4. Chạy toàn bộ test
pytest tests/ -v

# 5. Chạy pipeline end-to-end
python pipelines/run_end_to_end.py --config configs/data.yaml

# 6. Mở dashboard Streamlit
streamlit run app/dashboard.py
```

## Cấu trúc dự án

- `src/sales_forecast/` — Package chính (10 giai đoạn pipeline)
- `configs/` — Tham số cấu hình (YAML)
- `data/` — Dữ liệu: raw (bất biến) → interim → processed → predictions
- `pipelines/` — Script orchestration (điểm vào chạy end-to-end)
- `app/` — Dashboard Streamlit (5 tab: so sánh, dự báo, phân tích lỗi, SHAP, coverage)
- `tests/` — Unit test (đối xứng với `src/` và `app/`)
- `reports/` — Output (metrics, hình ảnh SHAP, trials Optuna)
- `docs/` — Tài liệu đặc tả kỹ thuật (8 mục + log quyết định)

Chi tiết: xem `docs/04_repo_structure.md`

## Tài liệu quan trọng

| File | Mục đích |
|------|---------|
| `docs/00_decisions.md` | Log quyết định kiến trúc đã chốt |
| `docs/01_ideation.md` | Bối cảnh, khảo sát data, framing bài toán |
| `docs/02_pipeline_architecture.md` | Sơ đồ giải thuật 10 giai đoạn + conformal |
| `docs/06_environment_setup.md` | Setup venv, xác thực, lock file |
| `docs/07_dashboard_spec.md` | Đặc tả dashboard Streamlit |
| `docs/08_uncertainty_conformal.md` | Split Conformal Prediction 95% |
| `CLAUDE.md` | Hướng dẫn cho AI coding assistant |

## Dữ liệu

Dataset từ **Kaggle Walmart Recruiting — Store Sales Forecasting**:
- `train.csv` — 421,570 dòng (2010–2012, 45 cửa hàng × 99 đơn vị bán hàng)
- `test.csv` — 115,064 dòng (2013, test set)
- `features.csv` — 8,190 dòng (đặc trưng macroeconomic)
- `stores.csv` — 45 dòng (thông tin cửa hàng)

**Lưu ý:** Có sales âm, MarkDown thiếu dữ liệu (MNAR). Xem chi tiết schema: `docs/03_data_io_diagram.md`

**Đơn vị dự báo (cập nhật 2026-08-19):** `(Store, Date)` — pipeline aggregate `Weekly_Sales` theo Dept ngay sau bước ingestion, không dự báo riêng theo từng Dept. Do đó project không còn tạo được `submission.csv` đúng format nộp Kaggle gốc; xem lý do và hệ quả đầy đủ ở `docs/00_decisions.md`.

## Model

5 model bắt buộc:
1. Naive 52 (baseline)
2. Decision Tree 
3. Random Forest
4. AdaBoost
5. XGBoost


Xem chi tiết: `docs/01_ideation.md`

## Bàn giao

- Code modular, test coverage ≥ 80%
- Báo cáo kỹ thuật (PDF): metrics, hình SHAP, phân tích lỗi
- Dashboard Streamlit tổng hợp (5 tab)
- Environment lock file: `docs/env_locks/environment_lock_<ngày>.txt`
- Demo theo link: https://aioconquermodule3porscheclub-eyiobj6myuqyqvaasnqvwh.streamlit.app/
## Liên hệ

Nếu có câu hỏi về kiến trúc hoặc pipeline, xem `docs/00_decisions.md` và `CLAUDE.md`.
