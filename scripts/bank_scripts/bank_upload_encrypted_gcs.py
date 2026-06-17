import os
import logging
import requests
import pandas as pd
from dotenv import load_dotenv, find_dotenv
from airflow.providers.google.cloud.hooks.gcs import GCSHook

# Load base config (.env with Docker container paths)
# (先加载基础配置，包含 Docker 容器路径)
load_dotenv(find_dotenv())

# Override with local config if it exists (.env.local with Mac absolute paths)
# (如果本地配置文件存在，用 Mac 绝对路径覆盖，供本地测试使用)
local_env = find_dotenv('.env.local')
if local_env:
    load_dotenv(local_env, override=True)

# Configure logging (配置日志记录器)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Directory configuration from environment variables (从环境变量读取目录配置)
STAGING_DIR = os.environ.get(
    "BANK_STAGING_DIR",
    "./data/1_staging/bank_staging"
)

# Service and GCS configuration (服务和 GCS 配置，非敏感信息直接硬编码)
ENCRYPT_API_URL = "http://encryption-service:8000/encrypt"
BUCKET_NAME = "dj-projects-storage"
GCS_OBJECT_PREFIX = "project1/bank_data"
GCP_CONN_ID = "gcp_gcs_conn"


def encrypt_and_upload_to_gcs() -> int:
    """
    Reads CSV files from bank_staging, hashes the customer_id column via
    the shared encryption service, and uploads to GCS.
    (从 bank_staging 读取 CSV 文件，通过共享加密服务对 customer_id 列进行哈希，然后上传到 GCS)

    Returns:
        int: Number of files successfully uploaded. (成功上传的文件数量)
    """
    try:
        # Validate staging directory exists (验证 staging 目录存在)
        if not os.path.exists(STAGING_DIR):
            logger.error(f"Staging directory not found (找不到 Staging 目录): {STAGING_DIR}")
            raise FileNotFoundError(f"Staging directory not found: {STAGING_DIR}")

        # Get valid CSV files only (只获取有效的 CSV 文件，过滤隐藏文件)
        valid_files = [
            f for f in os.listdir(STAGING_DIR)
            if f.endswith('.csv') and not f.startswith('.')
        ]

        if not valid_files:
            logger.info("No files found in bank_staging, nothing to upload (bank_staging 为空，无需上传)")
            return 0

        logger.info(f"Found {len(valid_files)} file(s) to process (发现 {len(valid_files)} 个文件待处理)")

        # Initialise GCS Hook via Airflow connection (通过 Airflow Connection 初始化 GCS Hook)
        gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        logger.info(f"GCS connection established via [{GCP_CONN_ID}] (GCS 连接成功)")

        uploaded_count = 0

        for file_name in valid_files:
            original_file_path = os.path.join(STAGING_DIR, file_name)
            logger.info(f"Processing file (正在处理文件): {file_name}")

            try:
                # Step 1: Read CSV into DataFrame (第一步：读取 CSV 文件)
                df = pd.read_csv(original_file_path)

                # Step 2: Hash customer_id column via encryption service
                # (第二步：通过加密服务对 customer_id 列进行哈希处理)
                if "customer_id" in df.columns:
                    raw_data = df["customer_id"].astype(str).tolist()
                    logger.info(f"Sending {len(raw_data)} records to encryption service (发送 {len(raw_data)} 条记录至加密服务)")

                    response = requests.post(
                        ENCRYPT_API_URL,
                        json={"data": raw_data},
                        timeout=30  # Prevent hanging requests (防止请求挂起)
                    )

                    if response.status_code == 200:
                        df["customer_id"] = response.json().get("result")
                        logger.info("Hashing successful, column replaced in memory (哈希成功，已在内存中替换原列)")
                    else:
                        logger.error(f"Encryption service returned error (加密服务返回错误): {response.status_code}")
                        continue  # Skip file to avoid uploading unhashed data (跳过此文件，避免上传未哈希数据)
                else:
                    logger.warning("'customer_id' column not found, uploading as-is ('customer_id' 列不存在，原样上传)")

                # Step 3: Write hashed data to temp file (第三步：将哈希后的数据写入临时文件)
                temp_file_path = f"/tmp/hashed_{file_name}"
                df.to_csv(temp_file_path, index=False)

                # Step 4: Upload temp file to GCS (第四步：上传临时文件到 GCS)
                object_name = f"{GCS_OBJECT_PREFIX}/hashed_{file_name}"
                gcs_hook.upload(
                    bucket_name=BUCKET_NAME,
                    object_name=object_name,
                    filename=temp_file_path,
                    mime_type="text/csv"
                )
                logger.info(f"Uploaded to GCS (已上传至 GCS): gs://{BUCKET_NAME}/{object_name}")

                # Step 5: Remove temp file (第五步：删除临时文件)
                os.remove(temp_file_path)
                logger.info(f"Temp file removed (临时文件已删除): {temp_file_path}")

                uploaded_count += 1

            except requests.exceptions.ConnectionError:
                # Raised when encryption service container is unreachable
                # (加密服务容器无法连接时抛出，给出明确报错)
                logger.error(f"Cannot reach encryption service at {ENCRYPT_API_URL} (无法连接加密服务，请确认容器是否正在运行)")
                raise
            except Exception as e:
                logger.error(f"Failed to process file (处理文件失败) {file_name}: {e}")
                raise

        logger.info(f"Upload complete. {uploaded_count} file(s) uploaded successfully (上传完成，共上传 {uploaded_count} 个文件)")
        return uploaded_count

    except Exception as e:
        logger.error(f"Unexpected error during upload process (上传过程中发生意外错误): {e}")
        raise


if __name__ == "__main__":
    encrypt_and_upload_to_gcs()