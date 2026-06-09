import os
import shutil

# 🌟 自动判断当前环境，实现路径自适应 (Airflow 容器 vs Mac 本地)
if os.path.exists('/opt/airflow'):
    # Airflow 容器内路径
    SOURCE_DIR = "/opt/airflow/data/1_landing/bank_landing"
    TARGET_DIR = "/opt/airflow/data/1_staging/bank_staging"
else:
    # Mac 本地测试路径
    SOURCE_DIR = "/Users/davy/airflow_davy/data/1_landing/bank_landing"
    TARGET_DIR = "/Users/davy/airflow_davy/data/1_staging/bank_staging"

def move_bank_data_to_staging():
    # 确保目标 Staging 文件夹存在，避免报错
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # 检查源 Landing 文件夹是否存在
    if not os.path.exists(SOURCE_DIR):
        print(f"⚠️ 源文件夹不存在，跳过本次操作: {SOURCE_DIR}")
        return

    # 扫描 Landing 区，筛选出所有的 CSV 文件
    files_to_move = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.csv')]
    
    if not files_to_move:
        print("📭 Landing 区目前为空，没有发现新的银行维度数据。")
        return

    print(f"📦 发现 {len(files_to_move)} 个银行数据文件，准备转移至 Staging 区...")

    # 执行原子转移
    for file_name in files_to_move:
        source_path = os.path.join(SOURCE_DIR, file_name)
        target_path = os.path.join(TARGET_DIR, file_name)
        
        try:
            # 核心操作：利用 shutil.move 实现系统级别的剪切粘贴
            shutil.move(source_path, target_path)
            print(f"✅ 成功转移: {file_name}")
        except Exception as e:
            # 捕获异常，防止某一个文件被占用导致整个流水线崩溃
            print(f"❌ 转移文件 {file_name} 时发生错误: {e}")

    print("🎉 银行维度数据已全部安全送达 bank_staging，等待下一步加密处理！\n")

if __name__ == "__main__":
    move_bank_data_to_staging()