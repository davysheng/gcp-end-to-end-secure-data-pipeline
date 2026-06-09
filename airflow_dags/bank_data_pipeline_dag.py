from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# 🌟 从你的 bank_scripts 文件夹中精确导入这四个函数
# （假设你脚本里的主函数名字是下面这些，如果名字不一样，请替换成你实际定义的函数名）
from scripts.bank_scripts.bank_generate import generate_daily_bank_customers
from scripts.bank_scripts.move_to_bank_staging import move_bank_data_to_staging
from scripts.bank_scripts.bank_encrypt_upload_gcs import encrypt_and_upload_bank_data
from scripts.bank_scripts.bank_staging_to_archive import move_staging_to_archive

# 1. 基础配置
default_args = {
    'owner': 'davy',
    'start_date': datetime(2026, 6, 1), 
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# 2. 实例化 DAG
with DAG(
    'bank_encryption_pipeline_python_v1', 
    default_args=default_args, 
    schedule='*/10 * * * *', # 手动触发 
    catchup=False,
    tags=['bank', 'python_operator', 'microservice']
) as dag:

    # 步骤 1：生成源数据
    step_1 = PythonOperator(
        task_id='generate_landing_data',
        python_callable=generate_daily_bank_customers
    )

    # 步骤 2：转移至 Staging 区
    step_2 = PythonOperator(
        task_id='move_data_to_staging',
        python_callable=move_bank_data_to_staging
    )

    # 步骤 3：调用加密微服务并直飞云端
    step_3 = PythonOperator(
        task_id='encrypt_and_upload_to_gcs',
        python_callable=encrypt_and_upload_bank_data
    )

    # 步骤 4：清理战场，移入归档区
    step_4 = PythonOperator(
        task_id='archive_staging_data',
        python_callable=move_staging_to_archive
    )

    # 完美的单线拓扑关系
    step_1 >> step_2 >> step_3 >> step_4