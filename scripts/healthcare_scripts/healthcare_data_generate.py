import os
import uuid
import random
import csv
from datetime import datetime
from faker import Faker

fake = Faker('en_AU')

# 自动感知环境
if os.path.exists('/opt/airflow'):
    LANDING_DIR = "/opt/airflow/data/1_landing/healthcare_landing"
    print("🌍 运行环境检测：Airflow 容器内")
else:
    LANDING_DIR = "/Users/davy/airflow_davy/data/1_landing/healthcare_landing"
    print("💻 运行环境检测：Mac 本地")

os.makedirs(LANDING_DIR, exist_ok=True)

def generate_daily_snapshot(num_patients=50):
    print("🚀 正在生成 Healthcare 每日全量快照 (Daily Snapshot)...")
    records = []
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    for _ in range(num_patients):
        records.append({
            'patient_uuid': str(uuid.uuid4()),
            'patient_name': fake.name(),
            'medicare_number': fake.bothify(text='##########'),
            'insurance_plan': random.choice(['Basic', 'Premium', 'Standard', 'Uninsured']),
            'start_date': today_str,
            'end_date': '9999-12-31' 
        })
        
    # 👇👇👇 核心修改：把写文件的逻辑直接包在函数内部 👇👇👇
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"healthcare_snapshot_{timestamp}.csv"
    file_path = os.path.join(LANDING_DIR, file_name)
    
    headers = ['patient_uuid', 'patient_name', 'medicare_number', 'insurance_plan', 'start_date', 'end_date']
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"✅ 成功生成 {len(records)} 条纯净快照数据！")
    print(f"📁 文件已落地至: {file_path}")
    
    # 返回一个成功状态或文件路径，而不是把 50 人的数据直接甩进内存
    return f"Success: Data written to {file_path}"

# 底部只留一个极简的本地测试入口
if __name__ == "__main__":
    generate_daily_snapshot(num_patients=50)