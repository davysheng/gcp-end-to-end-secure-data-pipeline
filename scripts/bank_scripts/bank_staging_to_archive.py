import os
import shutil
from datetime import datetime

# 1. 路径配置：精准定位 Staging 和 Archive 目录
if os.path.exists('/opt/airflow'):
    BASE_DIR = "/opt/airflow/data"
else:
    BASE_DIR = "/Users/davy/airflow_davy/data"

STAGING_DIR = os.path.join(BASE_DIR, "1_staging/bank_staging")
# 设定归档区路径，遵循你的分层架构
ARCHIVE_DIR = os.path.join(BASE_DIR, "1_archive/bank_archive")

def move_staging_to_archive():
    # 步骤 1：确保归档目录存在，如果没有则自动创建
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        print(f"📁 归档目录不存在，已自动创建: {ARCHIVE_DIR}")

    if not os.path.exists(STAGING_DIR):
        print(f"❌ 找不到银行 Staging 路径: {STAGING_DIR}")
        return

    files = os.listdir(STAGING_DIR)
    # 过滤掉隐藏文件，只认 CSV
    valid_files = [f for f in files if f.endswith('.csv') and not f.startswith('.')]

    if not valid_files:
        print("📭 银行 Staging 目录空空如也，没有需要归档的文件。")
        return

    print(f"📦 引擎启动！准备将 {len(valid_files)} 个未加密原始底稿转移至 Archive 归档区...")

    # 获取当前时间戳，精确到秒
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for file_name in valid_files:
        source_path = os.path.join(STAGING_DIR, file_name)
        
        # 步骤 2：给归档文件重命名，加上时间戳
        # 为什么要加？防止明天跑同一批任务时，归档区同名的旧文件被直接覆盖覆盖。
        name_part, ext_part = os.path.splitext(file_name)
        archive_file_name = f"{name_part}_{timestamp}{ext_part}"
        destination_path = os.path.join(ARCHIVE_DIR, archive_file_name)

        try:
            # 步骤 3：核心动作 —— 物理移动文件 (类似于剪切+粘贴)
            shutil.move(source_path, destination_path)
            print(f"✅ 成功归档: {file_name} -> {archive_file_name}")
        except Exception as e:
            print(f"❌ 归档文件 {file_name} 时发生系统错误: {e}")

    print("🎉 银行数据归档动作彻底完成！Staging 区已腾空，等待下一轮批处理指令。")

if __name__ == "__main__":
    print(">>> 正在以本地模式执行银行数据归档脚本...")
    move_staging_to_archive()