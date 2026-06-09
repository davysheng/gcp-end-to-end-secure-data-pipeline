import os
import pandas as pd
import requests
from airflow.providers.google.cloud.hooks.gcs import GCSHook

# 1. 路径配置: 兼容 Airflow 容器与本地测试环境
if os.path.exists('/opt/airflow'):
    STAGING_DIR = "/opt/airflow/data/1_staging/healthcare_staging"
else:
    STAGING_DIR = "/Users/davy/airflow_davy/data/1_staging/healthcare_staging"

# 2. 外部服务与 GCP 配置
ENCRYPT_API_URL = "http://encryption-service:8000/encrypt"
BUCKET_NAME = "dj-projects-storage"
GCP_CONN_ID = "gcp_gcs_conn"

# 🌟 核心定义: 需要被送入 Docker 进行加密的三大敏感列
TARGET_COLUMNS = ["patient_uuid", "patient_name", "medicare_number"]

def encrypt_and_upload_healthcare_data():
    if not os.path.exists(STAGING_DIR):
        print(f"❌ 找不到 Healthcare Staging 路径: {STAGING_DIR}")
        return

    files = os.listdir(STAGING_DIR)
    # 过滤隐藏文件，只认 CSV
    valid_files = [f for f in files if f.endswith('.csv') and not f.startswith('.')]

    if not valid_files:
        print("📭 Healthcare Staging 目录空空如也，没有需要处理的医疗数据。")
        return

    print(f"🚀 引擎启动！准备处理 {len(valid_files)} 个医疗数据文件...")

    try:
        # 召唤 GCSHook
        gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        # 获取 GCP Storage 底层 Client，用于实现真正的纯内存直传
        gcs_client = gcs_hook.get_conn()
        bucket = gcs_client.bucket(BUCKET_NAME)
        print(f"✅ 成功调用 Airflow Connection [{GCP_CONN_ID}] 连接 GCP！")
    except Exception as e:
        print(f"❌ 召唤 GCSHook 失败，请检查连接配置: {e}")
        return

    for file_name in valid_files:
        original_file_path = os.path.join(STAGING_DIR, file_name)
        print(f"\n---> 正在处理医疗文件: {file_name}")

        try:
            # 步骤 1: 读取 Staging 中的原始维度快照
            df = pd.read_csv(original_file_path)

            # 步骤 2: 循环将三个目标列依次发往 Docker 容器脱敏
            for col in TARGET_COLUMNS:
                if col in df.columns:
                    # 提取单列数据为字符串列表
                    raw_data = df[col].astype(str).tolist()
                    print(f"🔒 正在将 {len(raw_data)} 个 [{col}] 发送至加密容器...")
                    
                    response = requests.post(ENCRYPT_API_URL, json={"data": raw_data})
                    
                    if response.status_code == 200:
                        encrypted_data = response.json().get("result")
                        # 内存中直接完成该列的数据替换
                        df[col] = encrypted_data
                        print(f"  ✅ [{col}] 字段加密替换成功！")
                    else:
                        print(f"  ❌ [{col}] 加密服务调用失败，状态码: {response.status_code}")
                        raise Exception(f"Encryption failed for {col}")
                else:
                    print(f"⚠️ 文件中未发现目标列 [{col}]，已跳过。")

            # 步骤 3: 真正的零残留纯内存登云 (彻底抛弃 /tmp 临时文件)
            print("☁️ 正在将内存中的密文转换为数据流，直传 GCP...")
            # 将 DataFrame 转化为内存中的 CSV 字符串流
            csv_buffer = df.to_csv(index=False)
            
            # 拼装 GCP 目标路径 (对应你截图中的 project1/healthcare_data/)
            object_name = f"project1/healthcare_data/encrypted_{file_name}"
            blob = bucket.blob(object_name)
            
            # 调用底层 Client 直接上传字符串流
            blob.upload_from_string(csv_buffer, content_type="text/csv")
            
            print(f"☁️ [GCS SUCCESS] 医疗脱敏数据已成功登云 -> gs://{BUCKET_NAME}/{object_name}")

        except Exception as e:
            print(f"❌ 处理医疗文件 {file_name} 时发生系统级错误: {e}")

if __name__ == "__main__":
    print(">>> 正在以本地模式测试医疗数据的脱敏登云链路...")
    encrypt_and_upload_healthcare_data()