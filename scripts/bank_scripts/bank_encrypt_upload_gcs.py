import os
import pandas as pd
import requests
from airflow.providers.google.cloud.hooks.gcs import GCSHook

# 1. 路径配置：精准定位到银行数据的 Staging 目录
if os.path.exists('/opt/airflow'):
    STAGING_DIR = "/opt/airflow/data/1_staging/bank_staging"
else:
    STAGING_DIR = "/Users/davy/airflow_davy/data/1_staging/bank_staging"

# 2. 外部服务与 GCP 配置
# 假设你的 FastAPI 已经完美适配，这里可以调用通用的 encrypt 接口，或者你新写的 bank 专属接口
ENCRYPT_API_URL = "http://encryption-service:8000/encrypt" 
BUCKET_NAME = "dj-projects-storage"
GCP_CONN_ID = "gcp_gcs_conn"

def encrypt_and_upload_bank_data():
    if not os.path.exists(STAGING_DIR):
        print(f"❌ 找不到银行 Staging 路径: {STAGING_DIR}")
        return

    files = os.listdir(STAGING_DIR)
    valid_files = [f for f in files if f.endswith('.csv') and not f.startswith('.')]

    if not valid_files:
        print("📭 银行 Staging 目录空空如也，没有需要处理的客户维度数据。")
        return

    print(f"🏦 引擎启动！准备处理 {len(valid_files)} 个银行文件，执行脱敏并直飞云端...")

    try:
        # 召唤 GCSHook
        gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        print(f"✅ 成功调用 Airflow Connection [{GCP_CONN_ID}] 连接 GCP！")
    except Exception as e:
        print(f"❌ 召唤 GCSHook 失败，请检查连接配置: {e}")
        return

    for file_name in valid_files:
        original_file_path = os.path.join(STAGING_DIR, file_name)
        print(f"\n---> 正在处理银行文件: {file_name}")

        try:
            # 步骤 1：读取 Staging 中的原始银行维度数据
            df = pd.read_csv(original_file_path)

            # 步骤 2：提取核心高敏字段 customer_id
            if "customer_id" in df.columns:
                raw_data = df["customer_id"].tolist()
                
                print(f"🔒 正在将 {len(raw_data)} 个客户 ID 发送至加密容器进行哈希打码...")
                response = requests.post(ENCRYPT_API_URL, json={"data": raw_data})
                
                if response.status_code == 200:
                    encrypted_data = response.json().get("result")
                    # 无缝替换原列，此时 df 里的客户 ID 已全部脱敏
                    df["customer_id"] = encrypted_data
                    print("✅ 加密回执接收成功，已在内存中完成 customer_id 变异替换。")
                else:
                    print(f"❌ 加密服务调用失败，状态码: {response.status_code}")
                    continue 
            else:
                print("⚠️ 文件中未发现 'customer_id' 列，将原样上传。")

            # 步骤 3：零残留中转 —— 将密文存入系统级 /tmp 目录
            temp_file_path = f"/tmp/encrypted_{file_name}"
            df.to_csv(temp_file_path, index=False)

            # 步骤 4：直飞云端 —— 注意这里的 project1/bank_data/ 前缀隔离
            object_name = f"project1/bank_data/encrypted_{file_name}" 
            
            gcs_hook.upload(
                bucket_name=BUCKET_NAME,
                object_name=object_name,
                filename=temp_file_path,
                mime_type="text/csv"
            )
            print(f"☁️ [GCS SUCCESS] 银行脱敏维度表已成功登云 -> gs://{BUCKET_NAME}/{object_name}")

            # 步骤 5：阅后即焚 —— 抹除 /tmp 里的密文痕迹
            os.remove(temp_file_path)
            print("🧹 临时密文文件已物理销毁。Staging 目录内的原始文件保持安全隔离。")

        except Exception as e:
            print(f"❌ 处理银行文件 {file_name} 时发生系统错误: {e}")

if __name__ == "__main__":
    print(">>> 正在以本地模式测试银行数据的加密登云链路...")
    encrypt_and_upload_bank_data()