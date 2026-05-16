import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import date
import json, os, glob
from dotenv import load_dotenv

load_dotenv()

def load():
    # ── Đọc toàn bộ file clean thay vì chỉ hôm nay ─────────────────────────
    all_files = glob.glob("data/clean/*.csv")
    if not all_files:
        print(" Không có file nào trong data/clean/")
        return

    df = pd.concat([pd.read_csv(f) for f in all_files], ignore_index=True)

    # Xoá duplicate phòng chạy lại nhiều lần trong ngày
    df = df.drop_duplicates(subset=["city", "extracted_date"], keep="last")

    print(f" Tổng {len(df)} dòng từ {len(all_files)} file")

    # ── Kết nối BigQuery ────────────────────────────────────────────────────
    key_info = json.loads(os.environ["GCP_KEY_JSON"])
    credentials = service_account.Credentials.from_service_account_info(
        key_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    client = bigquery.Client(
        credentials=credentials,
        project=key_info["project_id"]
    )

    table_id = f"{key_info['project_id']}.weather_data.daily_weather"

    # ── WRITE_TRUNCATE: xoá toàn bộ bảng rồi ghi lại ──────────────────────
    # Không dùng DELETE vì free tier không cho phép DML
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True,
    )

    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    print(f" Đã load {len(df)} dòng lên BigQuery")
    print(f"   Bảng hiện có tổng cộng {table.num_rows} dòng")


if __name__ == "__main__":
    load()