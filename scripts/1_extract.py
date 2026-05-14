import dotenv
import requests
import pandas as pd
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv(override=True)  # Tự động load .env vào biến môi trường

# ── Danh sách các thành phố muốn theo dõi ──────────────────────────────────
CITIES = [
    "Ho Chi Minh City",
    "Hanoi",
    "Da Nang",
    "Can Tho",
    "Hue",
]

# ── Hàm gọi API cho một thành phố ──────────────────────────────────────────
def get_weather(city, api_key):
    """
    Gọi OpenWeather API, trả về dict chứa thông tin thời tiết.
    
    URL mẫu:
    https://api.openweathermap.org/data/2.5/weather?q=Hanoi&appid=KEY&units=metric
    
    units=metric → nhiệt độ trả về theo Celsius (không dùng thì ra Kelvin)
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",   # Celsius
        "lang": "vi"         # mô tả thời tiết bằng tiếng Việt
    }
    response = requests.get(url, params=params)
    
    # Nếu API trả lỗi (sai city name, hết quota...) thì dừng và báo lỗi
    response.raise_for_status()
    
    data = response.json()  # chuyển JSON thành dict Python
    
    # Trích xuất các trường quan trọng từ JSON lồng nhau
    return {
        "city":             city,
        "country":          data["sys"]["country"],
        "temp_c":           data["main"]["temp"],
        "feels_like_c":     data["main"]["feels_like"],
        "temp_min_c":       data["main"]["temp_min"],
        "temp_max_c":       data["main"]["temp_max"],
        "humidity_pct":     data["main"]["humidity"],
        "pressure_hpa":     data["main"]["pressure"],
        "weather_main":     data["weather"][0]["main"],
        "weather_desc":     data["weather"][0]["description"],
        "wind_speed_ms":    data["wind"]["speed"],
        "wind_deg":         data["wind"].get("deg", None),   # .get() vì đôi khi thiếu
        "cloudiness_pct":   data["clouds"]["all"],
        "visibility_m":     data.get("visibility", None),
        "extracted_at":     pd.Timestamp.utcnow().isoformat(),  # thời điểm lấy data
        "extracted_date":   date.today().isoformat(),           # ngày lấy data
    }


# ── Hàm chính ───────────────────────────────────────────────────────────────
def extract():
    # Đọc API key từ biến môi trường (không hardcode vào code!)
    # Khi chạy local: bạn set biến môi trường trên máy
    # Khi chạy GitHub Actions: nó đọc từ GitHub Secrets
    api_key = os.environ["OPENWEATHER_API_KEY"]
    
    rows = []
    for city in CITIES:
        try:
            row = get_weather(city, api_key)
            rows.append(row)
            print(f" {city}: {row['temp_c']}°C, {row['weather_desc']}")
        except Exception as e:
            # Nếu một thành phố lỗi thì bỏ qua, không dừng toàn bộ
            print(f" NO {city}: {e}")
    
    df = pd.DataFrame(rows)
    
    # Lưu vào Data Lake
    today = date.today().isoformat()  # "2025-05-13"
    os.makedirs("data/raw", exist_ok=True)
    path = f"data/raw/{today}.csv"
    df.to_csv(path, index=False)
    
    print(f"\n Đã lưu {len(df)} dòng vào {path}")
    print(df)


if __name__ == "__main__":
    extract()