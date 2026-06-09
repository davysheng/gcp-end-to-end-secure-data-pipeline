import os
import shutil

# 🌟 智能环境识别：完美兼容 Mac 本地右键测试 与 Airflow 容器内自动化调度
if os.path.exists('/opt/airflow'):
    # 🐳 如果是在 Airflow 容器内运行，走大本营的挂载绝对路径
    STAGING_DIR = "/opt/airflow/data/1_staging/game_staging"
    ARCHIVE_DIR = "/opt/airflow/data/1_archive/game_archive"
else:
    # 💻 如果是在你的 Mac 本地测试，走原生绝对路径
    STAGING_DIR = "/Users/davy/airflow_davy/data/1_staging/game_staging"
    ARCHIVE_DIR = "/Users/davy/airflow_davy/data/1_archive/game_archive"

def archive_original_data():
    # 1. 确保目标归档文件夹（后悔药库）存在
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    # 2. 扫描 Staging 暂存区
    if not os.path.exists(STAGING_DIR):
        print(f"❌ 找不到暂存路径: {STAGING_DIR}")
        return
        
    files = os.listdir(STAGING_DIR)
    # 严格过滤，只搬运 .csv 文件
    valid_files = [f for f in files if f.endswith('.csv') and not f.startswith('.')]

    if not valid_files:
        print("📭 Staging 暂存区已经清空，没有需要归档的文件。")
        return

    current_env = "Airflow 大本营容器" if os.path.exists('/opt/airflow') else "Mac 本地"
    print(f"📦 归档机器人启动！当前运行环境: [{current_env}]")
    print(f"发现 {len(valid_files)} 个原始明文文件，准备转移至历史后悔药库...\n")

    moved_count = 0
    for file_name in valid_files:
        src_path = os.path.join(STAGING_DIR, file_name)
        dest_path = os.path.join(ARCHIVE_DIR, file_name)
        
        try:
            # 🅰️ 核心动作：原子性移动（相当于 剪切 + 粘贴）
            shutil.move(src_path, dest_path)
            print(f"✅ [ARCHIVED] 原始明文已安全入库 ──► {file_name}")
            moved_count += 1
            
        except Exception as e:
            print(f"💥 归档文件 {file_name} 时发生异常: {e}")
            
    print(f"\n🎯 归档大功告成！共将 {moved_count} 个文件收入 Archive。")
    print("🧹 Staging 暂存区已彻底清空，随时准备迎接明天的新一波数据轰炸！")

if __name__ == "__main__":
    archive_original_data()