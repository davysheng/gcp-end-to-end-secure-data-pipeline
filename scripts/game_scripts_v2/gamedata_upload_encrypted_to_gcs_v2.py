import os
import pandas as pd
import requests
# 🌟 核心升级：直接引入 Airflow 原生的谷歌云钩子
from airflow.providers.google.cloud.hooks.gcs import GCSHook

# 1. 路径配置：这次我们的源头是 Staging 目录
if os.path.exists('/opt/airflow'):
    STAGING_DIR = "/opt/airflow/data/1_staging/game_staging"
else:
    STAGING_DIR = "/Users/davy/airflow_davy/data/1_staging/game_staging"

# 2. 外部服务与 GCP 配置
ENCRYPT_API_URL = "http://encryption-service:8000/encrypt" # 你的独立加密 Docker 地址
BUCKET_NAME = "dj-projects-storage"
GCP_CONN_ID = "gcp_gcs_conn" # Airflow UI 里配置的 Connection ID

def encrypt_and_upload_to_gcs():
    if not os.path.exists(STAGING_DIR):
        print(f"❌ 找不到 Staging 路径: {STAGING_DIR}")
        return

    files = os.listdir(STAGING_DIR)
    valid_files = [f for f in files if f.endswith('.csv') and not f.startswith('.')]

    if not valid_files:
        print("📭 Staging 目录空空如也，没有需要处理的文件。")
        return

    print(f"🚀 引擎启动！准备处理 {len(valid_files)} 个文件，执行加密并直飞云端...")

    try:
        # 魔法在这里：直接召唤 GCSHook
        gcs_hook = GCSHook(gcp_conn_id=GCP_CONN_ID)
        print(f"✅ 成功调用 Airflow Connection [{GCP_CONN_ID}] 连接谷歌云！")
    except Exception as e:
        print(f"❌ 召唤 GCSHook 失败，请检查 Airflow 环境或 Connection 配置: {e}")
        return

    for file_name in valid_files:
        original_file_path = os.path.join(STAGING_DIR, file_name)
        print(f"\n---> 正在处理文件: {file_name}")

        try:
            # 第一步：读取 Staging 中的原始文件
            df = pd.read_csv(original_file_path)

            # 第二步：检查并提取需要加密的列（假设这列叫 match_id）
            if "match_id" in df.columns:
                raw_data = df["match_id"].tolist()
                
                print(f"🔒 正在将 {len(raw_data)} 条记录发送至加密 Docker...")
                # 调用你写好的通用加密微服务
                response = requests.post(ENCRYPT_API_URL, json={"data": raw_data})
                
                if response.status_code == 200:
                    encrypted_data = response.json().get("result")
                    # 无缝替换原列，此时 df 已经是加密后的状态了
                    df["match_id"] = encrypted_data
                    print("✅ 加密回执接收成功，已在内存中替换原列。")
                else:
                    print(f"❌ 加密服务调用失败，状态码: {response.status_code}")
                    continue # 如果加密失败，跳过这个文件，防止原始数据意外上云
            else:
                print("⚠️ 文件中未发现 'match_id' 列，将原样上传。")

            # 第三步：将加密后的 DataFrame 存为一个【临时文件】
            # 我们把它放在 /tmp 目录下，绝对不污染 game_staging
            temp_file_path = f"/tmp/encrypted_{file_name}"
            df.to_csv(temp_file_path, index=False)

            # 第四步：将这个临时加密文件上传到 GCS
            object_name = f"project1/game_data/encrypted_{file_name}" # 在 GCS 上加上 encrypted_ 前缀以示区别
            
            gcs_hook.upload(
                bucket_name=BUCKET_NAME,
                object_name=object_name,
                filename=temp_file_path,
                mime_type="text/csv"
            )
            print(f"☁️ [GCS SUCCESS] 密文已成功登云 -> gs://{BUCKET_NAME}/{object_name}")

            # 第五步：阅后即焚
            os.remove(temp_file_path)
            print("🧹 临时密文文件已销毁。Staging 目录内的原始文件保持不变。")

        except Exception as e:
            print(f"❌ 处理文件 {file_name} 时发生系统错误: {e}")

if __name__ == "__main__":
    # 为了防止本地测试时污染真实的生产数据，也可以在这里加点测试提示
    print(">>> 正在以本地模式直接运行脚本当中...")
    encrypt_and_upload_to_gcs()