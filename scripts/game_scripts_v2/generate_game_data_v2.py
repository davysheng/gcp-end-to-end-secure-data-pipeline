import os
import csv
import uuid
import random
from datetime import datetime, timedelta

# 🌟 董组长看这里！自动判断当前是在 Mac 本地还是在 Airflow 容器内
if os.path.exists('/opt/airflow'):
    # 如果是在 Airflow 容器里运行，走虚拟世界的路径（通过 Docker 传送门直达本地 data）
    TARGET_DIR = "/opt/airflow/data/1_landing/game_landing"
else:
    # 如果是在你 Mac 本地手动右键测试，继续走你的原生绝对路径
    TARGET_DIR = "/Users/davy/airflow_davy/data/1_landing/game_landing"

def generate_daily_match_logs():
    # 自动检测并确保游戏落地文件夹存在
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 用“年月日_时分秒_微秒”动态命名，保证每运行一次都产生全新文件
    file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_name = f"game_logs_{file_timestamp}.csv"
    file_path = os.path.join(TARGET_DIR, file_name)

    # 🚀 拨乱反正：去掉拉链区间，恢复事实表的本来面貌
    headers = [
        "match_id", 
        "player_id", 
        "damage_dealt", 
        "match_duration_secs", 
        "match_timestamp"  # 替换为单一的事件时间戳
    ]

    # 每次运行随机产生 30 到 80 条对局日志
    num_rows = random.randint(30, 80)

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for _ in range(num_rows):
            match_id = str(uuid.uuid4())                     
            player_id = f"P{random.randint(10000, 15000)}"   
            damage_dealt = random.randint(800, 18500)        
            match_duration_secs = random.randint(900, 2400)  
            
            # ⏱️ 模拟对局发生的真实时间：当前时间减去随机的分钟数（过去24小时内）
            random_minutes_ago = random.randint(1, 1440)
            match_time = (datetime.now() - timedelta(minutes=random_minutes_ago)).strftime("%Y-%m-%d %H:%M:%S")
            
            writer.writerow([
                match_id, 
                player_id, 
                damage_dealt, 
                match_duration_secs, 
                match_time
            ])

    print(f"🚀 事实表数据重构成功落地！")
    print(f"新文件位置: {file_path}")
    print(f"包含字段: {headers}")
    print(f"本次生成行数: {num_rows} 行，已注入独立的对局时间戳\n")

if __name__ == "__main__":
    generate_daily_match_logs()