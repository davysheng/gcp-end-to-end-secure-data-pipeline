import os
import shutil
import glob
from datetime import datetime

# 🌟 依然保持环境自适应逻辑
if os.path.exists('/opt/airflow'):
    BASE_DIR = "/opt/airflow/data"
else:
    BASE_DIR = "/Users/davy/airflow_davy/data"

LANDING_DIR = os.path.join(BASE_DIR, "1_landing", "healthcare_landing")
STAGING_DIR = os.path.join(BASE_DIR, "1_staging", "healthcare_staging")

# 确保目标 Staging 文件夹存在
os.makedirs(STAGING_DIR, exist_ok=True)

def move_files_to_staging():
    # 查找 landing 目录下所有的 csv 文件
    files = glob.glob(os.path.join(LANDING_DIR, "*.csv"))
    
    if not files:
        print("⚠️ Landing 区没有发现待处理的 CSV 文件。")
        return

    print(f"📦 发现 {len(files)} 个待处理文件，准备移动...")
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(STAGING_DIR, file_name)
        
        # 移动文件
        shutil.move(file_path, dest_path)
        print(f"✅ 已成功移动: {file_name} -> 1_staging")

if __name__ == "__main__":
    move_files_to_staging()