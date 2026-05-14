import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import date
import json, os
from dotenv import load_dotenv

load_dotenv() 
def load():
    today = date.today().isoformat()
    clean_path = f"data/clean/{today}.csv"
    
    print(f" Đọc file sạch: {clean_path}")
    df = pd.read_csv(clean_path)
    # ── Kết nối BigQuery ────────────────────────────────────────────────────
    # Đọc key JSON từ biến môi trường (đã lưu trong GitHub Secrets)
    key_info = json.loads(os.environ["GCP_KEY_JSON"])
    
    credentials = service_account.Credentials.from_service_account_info(
        key_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    
    client = bigquery.Client(
        credentials=credentials,
        project=key_info["project_id"]
    )
    
    # ── Định nghĩa bảng đích ────────────────────────────────────────────────
    # Cú pháp: project_id.dataset_id.table_id
    table_id = f"{key_info['project_id']}.weather_data.daily_weather"
    
    # ── Cấu hình cách load ──────────────────────────────────────────────────
    job_config = bigquery.LoadJobConfig(
        # WRITE_APPEND = thêm dòng mới vào cuối, không xóa dữ liệu cũ
        # (nếu dùng WRITE_TRUNCATE thì sẽ xóa hết rồi ghi lại — không muốn vậy)
        write_disposition="WRITE_APPEND",
        autodetect=True,  # tự đoán kiểu dữ liệu của mỗi cột
    )
    
    # ── Đẩy dữ liệu lên ────────────────────────────────────────────────────
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()  # chờ job hoàn tất (blocking)
    
    # ── Xác nhận ────────────────────────────────────────────────────────────
    table = client.get_table(table_id)
    print(f" Đã load {len(df)} dòng lên BigQuery")
    print(f"   Bảng hiện có tổng cộng {table.num_rows} dòng")


if __name__ == "__main__":
    load()