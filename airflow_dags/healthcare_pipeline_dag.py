from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# 🌟 从你的 healthcare_scripts 文件夹中精确导入这四个核心函数
from scripts.healthcare_scripts.healthcare_data_generate import generate_daily_snapshot
from scripts.healthcare_scripts.move_to_healthcare_staging import move_files_to_staging
from scripts.healthcare_scripts.healthcare_encrypt_upload_gcs import encrypt_and_upload_healthcare_data
from scripts.healthcare_scripts.healthcare_staging_to_archive import archive_healthcare_data

# 1. 基础配置
default_args = {
    'owner': 'davy',
    'start_date': datetime(2026, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# 2. 实例化 DAG
with DAG(
    'healthcare_encryption_pipeline_python_v1',
    default_args=default_args,
    schedule='*/10 * * * *' ,  # 设定为每天跑一次，你也可以改成 '*/10 * * * *' 手动测试
    catchup=False,
    tags=['healthcare', 'python_operator', 'gcp', 'microservice']
) as dag:

    # 步骤 1：生成源数据 (每日快照)
    step_1 = PythonOperator(
        task_id='generate_landing_data',
        python_callable=generate_daily_snapshot
    )

    # 步骤 2：转移至 Staging 区
    step_2 = PythonOperator(
        task_id='move_data_to_staging',
        python_callable=move_files_to_staging
    )

    # 步骤 3：调用加密微服务并内存直飞云端 (零落盘)
    step_3 = PythonOperator(
        task_id='encrypt_and_upload_to_gcs',
        python_callable=encrypt_and_upload_healthcare_data
    )

    # 步骤 4：清理战场，移入归档区
    step_4 = PythonOperator(
        task_id='archive_staging_data',
        python_callable=archive_healthcare_data
    )

    # 3. 设定任务依赖顺序
    step_1 >> step_2 >> step_3 >> step_4