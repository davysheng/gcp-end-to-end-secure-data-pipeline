import os
import csv
import uuid
import random
from datetime import datetime, timedelta

# 🌟 董组长看这里！自动判断当前环境，实现路径自适应
if os.path.exists('/opt/airflow'):
    # Airflow 容器内路径
    TARGET_DIR = "/opt/airflow/data/1_landing/bank_landing"
else:
    # Mac 本地测试路径
    TARGET_DIR = "/Users/davy/airflow_davy/data/1_landing/bank_landing"

def generate_daily_bank_customers():
    # 确保银行数据的落地文件夹存在
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 动态命名，防止文件覆盖
    file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    file_name = f"bank_customers_{file_timestamp}.csv"
    file_path = os.path.join(TARGET_DIR, file_name)

    # 🚀 4个核心列 + 2个拉链时间区间
    headers = [
        "customer_id", 
        "account_tier", 
        "risk_level", 
        "credit_score", 
        "start_date", 
        "end_date"
    ]

    # 每次生成 20 到 50 个客户的状态快照
    num_rows = random.randint(20, 50)
    
    # 拉链表专属的“无穷远”结束时间
    active_end_date = "9999-12-31"

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        for _ in range(num_rows):
            # 生成模拟数据
            customer_id = f"CUST-{uuid.uuid4().hex[:8].upper()}"
            account_tier = random.choice(["Standard", "Gold", "Platinum"])
            # 故意让低风险占多数，高风险占少数，模拟真实业务分布
            risk_level = random.choices(["Low", "Medium", "High"], weights=[70, 20, 10], k=1)[0]
            credit_score = random.randint(300, 850)
            
            # 随机生成过去 1-5 天内的某一天作为状态生效日期
            random_days_ago = random.randint(1, 5)
            start_date = (datetime.now() - timedelta(days=random_days_ago)).strftime("%Y-%m-%d")
            
            writer.writerow([
                customer_id, 
                account_tier, 
                risk_level, 
                credit_score, 
                start_date, 
                active_end_date
            ])

    print(f"🏦 银行维度表（前菜）已备好！")
    print(f"新文件位置: {file_path}")
    print(f"包含字段: {headers}")
    print(f"本次生成行数: {num_rows} 行，等待 FastAPI 处理...\n")

if __name__ == "__main__":
    generate_daily_bank_customers()