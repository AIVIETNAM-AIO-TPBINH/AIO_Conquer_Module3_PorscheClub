import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import joblib

# -----------------------------------------------------------------------------
# 1. CẤU HÌNH GIAO DIỆN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Walmart Sales Forecasting Engine",
    page_icon="🛒",
    layout="wide"
)

st.markdown("""
<style>
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Hàm tìm file model tự động
def get_model_file(filename):
    if not filename:
        return None
    for root in [Path.cwd()] + list(Path.cwd().parents) + list(Path.cwd().glob("**/")):
        target = root / filename
        if target.is_file():
            return target
    return None

# -----------------------------------------------------------------------------
# 2. THÔNG TIN BENCHMARK MÔ HÌNH
# -----------------------------------------------------------------------------
MODEL_METRICS = {
    "xgb": {
        "name": "XGBoost · Champion Model",
        "val_mae": 44891.18,
        "val_wape": 0.0440,
        "cv_mae": 101968.95,
        "file": "models/xgb_direct_models.joblib",
        "desc": "Thuật toán Gradient Boosting đạt hiệu năng cao nhất trên tập Val."
    },
    "rf": {
        "name": "Random Forest · Ensemble Baseline",
        "val_mae": 50093.06,
        "val_wape": 0.0490,
        "cv_mae": 105654.24,
        "file": "models/rf_direct_models.joblib",
        "desc": "Mô hình rừng cây phân tán ổn định cao."
    },
    "naive52": {
        "name": "Naive 52 · Seasonal Baseline",
        "val_mae": 54159.11,
        "val_wape": 0.0530,
        "cv_mae": 58924.38,
        "file": None,
        "desc": "Heuristic lấy doanh số cùng kỳ năm ngoái (Lag 52)."
    },
    "dt": {
        "name": "Decision Tree · Single Tree",
        "val_mae": 65256.55,
        "val_wape": 0.0639,
        "cv_mae": 127737.90,
        "file": "models/dt_direct_models.joblib",
        "desc": "Cây quyết định đơn lẻ max_depth=12."
    },
    "ada": {
        "name": "AdaBoost Regressor",
        "val_mae": 122232.62,
        "val_wape": 0.1197,
        "cv_mae": 141850.94,
        "file": "models/ada_direct_models.joblib",
        "desc": "Mô hình Adaptive Boosting."
    }
}

# -----------------------------------------------------------------------------
# 3. SIDEBAR: CHỌN MÔ HÌNH
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### **Mô hình Dự báo**")
    selected_key = st.selectbox(
        "Pipeline mô hình",
        options=list(MODEL_METRICS.keys()),
        format_func=lambda x: MODEL_METRICS[x]["name"],
        index=0
    )
    current_model = MODEL_METRICS[selected_key]
    st.caption(current_model["desc"])
    st.divider()
    st.metric(
        label="Validation MAE",
        value=f"${current_model['val_mae']:,.0f}",
        delta=f"WAPE: {current_model['val_wape']*100:.2f}%",
        delta_color="inverse"
    )
    st.markdown(f"<small>CV 5-Fold MAE: <b>${current_model['cv_mae']:,.0f}</b></small>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. GIAO DIỆN CHÍNH
# -----------------------------------------------------------------------------
st.markdown("# 🛒 Walmart Store Sales Forecasting Engine")
st.markdown("**Hệ thống Dự báo Doanh số Cấp Cửa hàng** · Horizon $t+1 \\to t+10$ · Hỗ trợ Nạp Tệp Hàng Loạt")

tab1, tab2 = st.tabs(["📁 Nạp Tệp Dữ liệu Dự báo (Batch CSV)", "🎯 Nhập tay từng Cửa hàng (Single Input)"])

# =============================================================================
# TAB 1: NẠP TỆP DỮ LIỆU CSV (UPLOAD FILE DỰ BÁO HÀNG LOẠT)
# =============================================================================
with tab1:
    st.markdown("### **Tải lên tệp dữ liệu kiểm thử hoặc tương lai**")
    st.caption("Bạn có thể tải lên tệp `val_set.csv` (450 dòng) hoặc `test_final.csv` (1,755 dòng) để mô hình xử lý.")

    uploaded_file = st.file_uploader("Chọn file CSV từ máy tính của bạn", type=["csv"])

    if uploaded_file is not None:
        df_input = pd.read_csv(uploaded_file)
        st.success(f"✅ Đã nạp thành công tệp: `{uploaded_file.name}` ({len(df_input)} dòng, {len(df_input.columns)} cột).")

        with st.expander("👁️ Xem trước 5 dòng đầu tiên của tệp nạp vào"):
            st.dataframe(df_input.head(5), use_container_width=True)

        # Chọn Horizon dự báo tương ứng với tệp nạp
        batch_horizon = st.slider("Chọn tầm dự báo áp dụng (Horizon t+h)", min_value=1, max_value=10, value=1, key="batch_hz")

        if st.button("🚀 Tiến hành Dự báo Toàn bộ Tệp", type="primary", key="btn_batch"):
            with st.spinner("Đang chạy mô hình dự báo qua các dòng dữ liệu..."):
                results_df = df_input.copy()

                # Dự đoán theo mô hình được chọn
                if selected_key == "naive52":
                    results_df["Predicted_Sales"] = results_df["Lag_52"]
                else:
                    model_path = get_model_file(current_model["file"])
                    if model_path and model_path.exists():
                        loaded_models = joblib.load(model_path)
                        model_h = loaded_models[batch_horizon - 1]

                        # Chuẩn bị cột đầu vào cho mô hình
                        input_features = [
                            'Store', 'IsHoliday', 'Size', 'Temperature', 'Fuel_Price',
                            'MarkDown1', 'MarkDown2', 'MarkDown3', 'MarkDown4', 'MarkDown5',
                            'CPI', 'Unemployment', 'Lag_1', 'Lag_4', 'Lag_12', 'Lag_52',
                            'Rolling_Mean_4w', 'Year', 'Month', 'WeekOfYear', 'Type_encoded'
                        ]
                        
                        # Bổ sung các biến lịch tuần đích nếu thiếu
                        for col in input_features:
                            if col not in results_df.columns:
                                results_df[col] = 0

                        X_batch = results_df[input_features].copy()
                        X_batch["hol_t"] = results_df["IsHoliday"]
                        X_batch["woy_t"] = results_df["WeekOfYear"] if "WeekOfYear" in results_df.columns else 35
                        X_batch["mon_t"] = results_df["Month"] if "Month" in results_df.columns else 9

                        results_df["Predicted_Sales"] = model_h.predict(X_batch)
                    else:
                        st.warning("Không tìm thấy tệp model đã lưu. Đang sử dụng Heuristic Fallback.")
                        results_df["Predicted_Sales"] = 0.75 * results_df["Lag_52"] + 0.25 * results_df["Rolling_Mean_4w"]

                # Hiển thị thống kê tổng quan
                st.markdown("---")
                st.markdown("### **Kết quả Phân tích sau Dự báo**")
                
                sum_pred = results_df["Predicted_Sales"].sum()
                mean_pred = results_df["Predicted_Sales"].mean()

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    st.metric(label="Tổng Doanh số Dự báo", value=f"${sum_pred:,.2f}")
                with bcol2:
                    st.metric(label="Doanh số Trung bình / Tuần / Store", value=f"${mean_pred:,.2f}")

                # Nếu tệp nạp vào có cột nhãn thực tế 'Weekly_Sales' (như val_set.csv) -> tính sai số thực tế
                if "Weekly_Sales" in results_df.columns and results_df["Weekly_Sales"].notna().any() and (results_df["Weekly_Sales"] > 0).any():
                    valid_mask = results_df["Weekly_Sales"].notna() & (results_df["Weekly_Sales"] > 0)
                    y_true = results_df.loc[valid_mask, "Weekly_Sales"]
                    y_pred = results_df.loc[valid_mask, "Predicted_Sales"]

                    mae_actual = np.mean(np.abs(y_true - y_pred))
                    wape_actual = np.sum(np.abs(y_true - y_pred)) / np.sum(y_true) * 100

                    st.markdown("#### 🎯 **Đối soát với Nhãn Thực tế (Actual vs Predicted)**")
                    mcol1, mcol2 = st.columns(2)
                    with mcol1:
                        st.metric(label="MAE Thực tế trên Tệp này", value=f"${mae_actual:,.2f}")
                    with mcol2:
                        st.metric(label="WAPE Sai số Thực tế", value=f"{wape_actual:.2f}%")

                    # Biểu đồ so sánh Actual vs Pred
                    chart_compare = results_df.loc[valid_mask, ["Weekly_Sales", "Predicted_Sales"]].reset_index(drop=True)
                    st.line_chart(chart_compare.head(45), use_container_width=True)
                    st.caption("Biểu đồ so sánh Thực tế (Weekly_Sales) vs Dự báo (Predicted_Sales) trên 45 Cửa hàng đầu tiên.")

                # Cho phép tải tệp kết quả về máy
                csv_download = results_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Tải xuống Tệp Kết quả Dự báo (.csv)",
                    data=csv_download,
                    file_name=f"predicted_{selected_key}_{uploaded_file.name}",
                    mime="text/csv",
                    type="secondary"
                )

# =============================================================================
# TAB 2: DỰ BÁO TỪNG CỬA HÀNG (NHẬP TAY THAM SỐ)
# =============================================================================
with tab2:
    st.markdown("### **Thông tin Cửa hàng & Tham số Tuần đích**")

    col1, col2, col3 = st.columns(3)
    with col1:
        store_id = st.number_input("Mã cửa hàng (Store ID)", min_value=1, max_value=45, value=1, step=1)
        horizon = st.slider("Tầm dự báo (Horizon)", min_value=1, max_value=10, value=1)
        store_size = st.slider("Diện tích mặt bằng (sq ft)", min_value=30000, max_value=220000, value=151315, step=1000)
        store_type = st.selectbox("Phân loại mặt bằng", ["Type A", "Type B", "Type C"])

    with col2:
        is_holiday = st.radio("Tuần dự báo có ngày lễ? (IsHoliday)", [0, 1], format_func=lambda x: "Không" if x == 0 else "Có", horizontal=True)
        cpi = st.number_input("Chỉ số CPI", min_value=120.0, max_value=230.0, value=173.2, step=0.1)
        unemployment = st.slider("Tỷ lệ thất nghiệp (%)", min_value=3.0, max_value=15.0, value=7.8, step=0.1)
        fuel_price = st.number_input("Giá nhiên liệu ($/gallon)", min_value=2.0, max_value=5.0, value=3.63, step=0.05)

    with col3:
        lag_52 = st.number_input("Doanh số cùng kỳ năm ngoái - Lag_52 ($)", min_value=100000.0, max_value=4000000.0, value=1643690.0, step=10000.0)
        rolling_4w = st.number_input("Trung bình trượt 4 tuần gần nhất ($)", min_value=100000.0, max_value=4000000.0, value=1450000.0, step=10000.0)
        lag_1 = st.number_input("Doanh số tuần gần nhất - Lag_1 ($)", min_value=100000.0, max_value=4000000.0, value=1550000.0, step=10000.0)
        temperature = st.slider("Nhiệt độ trung bình (°F)", min_value=-5.0, max_value=105.0, value=65.0, step=1.0)

    st.markdown("---")
    if st.button("🚀 Dự báo Doanh số Cửa hàng Này", type="primary", use_container_width=True):
        if selected_key == "naive52":
            pred_sales = lag_52
        else:
            model_path = get_model_file(current_model["file"])
            if model_path and model_path.exists():
                models_list = joblib.load(model_path)
                model_h = models_list[horizon - 1]
                type_enc = 0 if "Type A" in store_type else (1 if "Type B" in store_type else 2)
                target_woy = 33 + horizon
                input_df = pd.DataFrame([{
                    "Store": store_id, "IsHoliday": is_holiday, "Size": store_size,
                    "Temperature": temperature, "Fuel_Price": fuel_price,
                    "MarkDown1": 0.0, "MarkDown2": 0.0, "MarkDown3": 0.0, "MarkDown4": 0.0, "MarkDown5": 0.0,
                    "CPI": cpi, "Unemployment": unemployment,
                    "Lag_1": lag_1, "Lag_4": rolling_4w, "Lag_12": rolling_4w, "Lag_52": lag_52,
                    "Rolling_Mean_4w": rolling_4w, "Year": 2012, "Month": 8 + (horizon // 4),
                    "WeekOfYear": target_woy, "Type_encoded": type_enc,
                    "hol_t": is_holiday, "woy_t": target_woy, "mon_t": 8 + (horizon // 4)
                }])
                pred_sales = float(model_h.predict(input_df)[0])
            else:
                pred_sales = (0.75 * lag_52 + 0.25 * rolling_4w)

        st.markdown(f"### **Kết quả Dự báo Doanh số Tuần t+{horizon}**")
        out1, out2, out3 = st.columns(3)
        diff_lag52 = ((pred_sales - lag_52) / lag_52) * 100
        with out1:
            st.metric(label=f"Dự báo Doanh số ({selected_key.upper()})", value=f"${pred_sales:,.2f}", delta=f"{diff_lag52:+.2f}% so với cùng kỳ")
        with out2:
            st.metric(label="Doanh số Cùng kỳ (Lag_52)", value=f"${lag_52:,.2f}")
        with out3:
            st.metric(label="Doanh số Tuần trước (Lag_1)", value=f"${lag_1:,.2f}")

        chart_df = pd.DataFrame({
            "Mốc": [f"Tuần trước (Lag 1)", f"Dự báo t+{horizon}", "Cùng kỳ năm ngoái (Lag 52)"],
            "Doanh số ($)": [lag_1, pred_sales, lag_52]
        })
        st.bar_chart(chart_df, x="Mốc", y="Doanh số ($)", use_container_width=True)