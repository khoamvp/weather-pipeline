import pandas as pd
from datetime import date
import os

def transform():
    today = date.today().isoformat()
    raw_path = f"data/raw/{today}.csv"
    
    print(f" Đọc file: {raw_path}")
    df = pd.read_csv(raw_path)
    
    print(f"   Shape ban đầu: {df.shape}")
    print(f"\n--- Kiểm tra missing values ---")
    print(df.isnull().sum())
    
    # ── 1. Xử lý missing values ─────────────────────────────────────────────
    # wind_deg và visibility đôi khi OpenWeather không trả về → điền 0
    df["wind_deg"]     = df["wind_deg"].fillna(0)
    df["visibility_m"] = df["visibility_m"].fillna(0)
    
    # ── 2. Kiểm tra giá trị hợp lệ ──────────────────────────────────────────
    # Nhiệt độ Việt Nam không thể âm sâu hay trên 50°C
    invalid_temp = df[(df["temp_c"] < -10) | (df["temp_c"] > 50)]
    if len(invalid_temp) > 0:
        print(f"\n  Nhiệt độ bất thường:\n{invalid_temp[['city','temp_c']]}")
    
    # Humidity phải trong [0, 100]
    df["humidity_pct"] = df["humidity_pct"].clip(0, 100)
    
    # ── 3. Chuẩn hóa kiểu dữ liệu ───────────────────────────────────────────
    df["extracted_at"]   = pd.to_datetime(df["extracted_at"])
    df["extracted_date"] = pd.to_datetime(df["extracted_date"]).dt.date
    
    # Làm tròn nhiệt độ 1 chữ số thập phân cho gọn
    for col in ["temp_c", "feels_like_c", "temp_min_c", "temp_max_c"]:
        df[col] = df[col].round(1)
    
    # ── 4. Thêm cột tính toán mới ────────────────────────────────────────────
    # Heat index đơn giản: cảm giác nóng hơn khi humidity cao
    df["heat_index"] = (
        df["temp_c"] + 0.33 * (df["humidity_pct"] / 100 * 6.105) - 4
    ).round(1)
    
    # Phân loại thời tiết
    def categorize(row):
        if row["temp_c"] >= 35:
            return "rất nóng"
        elif row["temp_c"] >= 30:
            return "nóng"
        elif row["temp_c"] >= 20:
            return "mát"
        else:
            return "lạnh"
    
    df["temp_category"] = df.apply(categorize, axis=1)
    
    # ── 5. Lưu kết quả ──────────────────────────────────────────────────────
    os.makedirs("data/clean", exist_ok=True)
    clean_path = f"data/clean/{today}.csv"
    df.to_csv(clean_path, index=False)
    
    print(f"\n Đã lưu {len(df)} dòng sạch vào {clean_path}")
    print(df[["city", "temp_c", "humidity_pct", "weather_desc", "temp_category"]])


if __name__ == "__main__":
    transform()