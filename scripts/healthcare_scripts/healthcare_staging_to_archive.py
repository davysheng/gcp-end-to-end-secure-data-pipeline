import os
import shutil
import glob

# 🌟 保持路径的自适应，完美兼容你的 Mac 本地与 Airflow 容器
if os.path.exists('/opt/airflow'):
    BASE_DIR = "/opt/airflow/data"
else:
    BASE_DIR = "/Users/davy/airflow_davy/data"

STAGING_DIR = os.path.join(BASE_DIR, "1_staging", "healthcare_staging")
ARCHIVE_DIR = os.path.join(BASE_DIR, "1_archive", "healthcare_archive")

# 确保目标 Archive 文件夹存在，没有会自动创建
os.makedirs(ARCHIVE_DIR, exist_ok=True)

def archive_healthcare_data():
    if not os.path.exists(STAGING_DIR):
        print(f"❌ 找不到 Healthcare Staging 路径: {STAGING_DIR}")
        return

    # 查找 staging 目录下所有的 csv 文件
    files = glob.glob(os.path.join(STAGING_DIR, "*.csv"))
    
    if not files:
        print("📭 Staging 区空空如也，没有需要归档的文件。")
        return

    print(f"📦 发现 {len(files)} 个已处理完毕的文件，准备进行安全归档...")
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        dest_path = os.path.join(ARCHIVE_DIR, file_name)
        
        # 将原始明文底稿移入归档区
        shutil.move(file_path, dest_path)
        print(f"✅ 成功归档底稿: {file_name} -> 2_archive")

if __name__ == "__main__":
    print(">>> 启动清理与归档程序...")
    archive_healthcare_data()