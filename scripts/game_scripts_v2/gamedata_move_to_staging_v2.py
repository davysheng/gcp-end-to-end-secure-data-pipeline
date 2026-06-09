import os
import shutil

# 🌟 董组长看这里！自动判断当前是在 Mac 本地还是在 Airflow 容器内
# 这一次我们把 LANDING_DIR 和 STAGING_DIR 都配齐，彻底消灭黄色波浪线！
if os.path.exists('/opt/airflow'):
    # 如果是在 Airflow 容器里运行，走虚拟世界的路径（通过 Docker 传送门直达本地 data）
    LANDING_DIR = "/opt/airflow/data/1_landing/game_landing"
    STAGING_DIR = "/opt/airflow/data/1_staging/game_staging"
else:
    # 如果是在你 Mac 本地手动右键测试，继续走你的原生绝对路径
    LANDING_DIR = "/Users/davy/airflow_davy/data/1_landing/game_landing"
    STAGING_DIR = "/Users/davy/airflow_davy/data/1_staging/game_staging"


def transfer_landing_to_staging():
    # 1. 自动检测并确保 game_staging 目标文件夹存在
    os.makedirs(STAGING_DIR, exist_ok=True)

    # 2. 读取当前 landing 里的所有内容
    try:
        files = os.listdir(LANDING_DIR)
    except FileNotFoundError:
        print(f"❌ 找不到源文件夹: {LANDING_DIR}, 请检查路径！")
        return

    # 3. 过滤出隐藏文件或空目录，只拿真正的文件
    valid_files = [f for f in files if os.path.isfile(os.path.join(LANDING_DIR, f)) and not f.startswith('.')]

    if not valid_files:
        print("📭 game_landing 文件夹里面空空如也，没有需要转移的文件。")
        return

    print(f"🔄 发现 {len(valid_files)} 个待处理的游戏对局文件，开始向暂存层 (Staging) 搬运...\n")

    moved_count = 0
    for file_name in valid_files:
        src_path = os.path.join(LANDING_DIR, file_name)
        dest_path = os.path.join(STAGING_DIR, file_name)

        # 4. 执行原子性移动（相当于剪切 + 粘贴），速度极快且安全
        shutil.move(src_path, dest_path)
        print(f"📦 [SUCCESS] 已成功移动: {file_name} ──► game_staging/")
        moved_count += 1

    print(f"\n✨ 暂存层转运大功告成！本次共清理并转移了 {moved_count} 个数据文件。")
    print("现在 game_landing 层已安全清空，随时准备迎接下一批新数据的轰炸。")


if __name__ == "__main__":
    transfer_landing_to_staging()