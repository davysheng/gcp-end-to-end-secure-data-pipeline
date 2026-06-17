import os
import io
import csv
import logging
import functions_framework
from google.cloud import bigquery, storage

# Configure logging (配置日志记录器)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Read environment variables set in Cloud Run console
# (从 Cloud Run 控制台配置的环境变量中读取项目配置)
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

# Routing table: maps GCS path prefix to BigQuery dataset and table
# (路由表：根据 GCS 路径前缀判断写入哪个 BigQuery 表)
ROUTE_MAP = {
    "project1/game_data/": {
        "dataset": "dj_project1_game",
        "table": "game_logs"
    },
    "project1/bank_data/": {
        "dataset": "dj_project1_bank",
        "table": "bank_customers"
    },
    "project1/healthcare_data/": {
        "dataset": "dj_project1_healthcare",
        "table": "healthcare_records"
    }
}


def detect_domain(file_path: str) -> dict | None:
    """
    Detects which domain the GCS file belongs to based on its path.
    (根据 GCS 文件路径判断属于哪个业务域)

    Returns the matching route config, or None if no match found.
    (返回对应的路由配置，找不到则返回 None)
    """
    for prefix, config in ROUTE_MAP.items():
        if file_path.startswith(prefix):
            return config
    return None


def load_csv_to_bigquery(
    bucket_name: str,
    file_path: str,
    dataset: str,
    table: str
) -> int:
    """
    Downloads a CSV file from GCS, parses it, and appends rows to BigQuery.
    (从 GCS 下载 CSV 文件，解析后追加写入 BigQuery 表)

    Returns the number of rows inserted. (返回写入的行数)
    """
    # Download CSV content from GCS (从 GCS 下载 CSV 文件内容)
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    content = blob.download_as_text(encoding="utf-8")

    # Parse CSV into list of dicts (解析 CSV 为字典列表，每行一个字典)
    reader = csv.DictReader(io.StringIO(content))
    rows = [dict(row) for row in reader]

    if not rows:
        logger.warning(f"CSV file is empty, skipping BQ insert (文件为空，跳过写入): {file_path}")
        return 0

    # Insert rows into BigQuery (写入 BigQuery)
    bq_client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{dataset}.{table}"

    errors = bq_client.insert_rows_json(table_ref, rows)

    if errors:
        raise RuntimeError(
            f"BigQuery insert errors for {table_ref} (写入 BigQuery 时发生错误): {errors}"
        )

    logger.info(f"Successfully inserted {len(rows)} rows into {table_ref} (成功写入行数)")
    return len(rows)

def delete_gcs_file(bucket_name: str, file_path: str) -> None:
    """
    Deletes the processed file from GCS after successful BigQuery load.
    (BigQuery 写入成功后，删除 GCS 中已处理的文件)
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_path)
    blob.delete()
    logger.info(f"Deleted GCS file after successful load (成功写入后删除 GCS 文件): {file_path}")


@functions_framework.cloud_event
def route_gcs_to_bigquery(cloud_event):
    """
    Entry point triggered by Eventarc when a new file is uploaded to GCS.
    (Eventarc 触发的入口函数，GCS 有新文件上传时自动调用)

    Flow: detect domain → load CSV to BigQuery → delete GCS file
    (流程：判断业务域 → 写入 BigQuery → 删除 GCS 文件)
    """
    try:
        # Extract file metadata from the CloudEvent payload
        # (从 CloudEvent 的 payload 中提取文件元数据)
        data = cloud_event.data
        file_path = data["name"]       # GCS object path (GCS 对象路径)
        bucket_name = data["bucket"]   # GCS bucket name (GCS bucket 名称)

        logger.info(f"Received GCS event for file (收到 GCS 文件上传事件): {file_path}")

        # Detect which domain this file belongs to (判断文件属于哪个业务域)
        route = detect_domain(file_path)

        if route is None:
            logger.warning(
                f"No matching route found, skipping file (未找到匹配路由，跳过): {file_path}"
            )
            return "No route matched", 200

        dataset = route["dataset"]
        table = route["table"]
        logger.info(f"Routing to (路由目标): {PROJECT_ID}.{dataset}.{table}")

        # Load CSV to BigQuery (写入 BigQuery)
        rows_inserted = load_csv_to_bigquery(bucket_name, file_path, dataset, table)

        # Delete GCS file only after successful insert
        # (只有写入成功后才删除 GCS 文件，防止数据丢失)
        delete_gcs_file(bucket_name, file_path)

        return f"Success: {rows_inserted} rows inserted into {dataset}.{table}", 200

    except Exception as e:
        logger.error(f"Unexpected error processing GCS event (处理 GCS 事件时发生意外错误): {e}")
        raise
