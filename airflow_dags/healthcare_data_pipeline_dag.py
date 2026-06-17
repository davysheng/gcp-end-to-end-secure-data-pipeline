from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Default arguments applied to all tasks (所有任务的默认配置)
default_args = {
    'owner': 'davy',
    'start_date': datetime(2026, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='healthcare_data_security_pipeline_v1',
    default_args=default_args,
    schedule='@daily',
    catchup=False,              # Prevent backfill runs (防止历史补跑)
    max_active_runs=1,          # Prevent concurrent runs competing for same files (防止并发抢文件)
    tags=['healthcare', 'pipeline']
) as dag:

    def run_generate_landing_data():
        # Import inside wrapper to isolate import errors from DAG loading
        # (import 放在 wrapper 内部，防止单脚本报错导致整个 DAG 不可见)
        from scripts.healthcare_scripts.healthcare_generate import generate_daily_healthcare_records
        return generate_daily_healthcare_records()

    def run_transfer_landing_to_staging():
        from scripts.healthcare_scripts.healthcare_moveto_staging import transfer_landing_to_staging
        return transfer_landing_to_staging()

    def run_encrypt_and_upload_to_gcs():
        from scripts.healthcare_scripts.healthcare_upload_encrypted_gcs import encrypt_and_upload_to_gcs
        return encrypt_and_upload_to_gcs()

    def run_archive_original_data():
        from scripts.healthcare_scripts.healthcare_archive import archive_original_data
        return archive_original_data()

    # Step 1: Generate raw patient records into landing directory
    # (步骤一：生成原始患者记录到 landing 目录)
    step_1 = PythonOperator(
        task_id='generate_landing_data',
        python_callable=run_generate_landing_data
    )

    # Step 2: Move CSV files from landing to staging
    # (步骤二：将 CSV 文件从 landing 移动到 staging)
    step_2 = PythonOperator(
        task_id='move_data_to_staging',
        python_callable=run_transfer_landing_to_staging
    )

    # Step 3: Hash sensitive columns and upload to GCS
    # (步骤三：对敏感字段进行哈希处理并上传到 GCS)
    step_3 = PythonOperator(
        task_id='encrypt_and_upload_to_gcs',
        python_callable=run_encrypt_and_upload_to_gcs
    )

    # Step 4: Archive original unencrypted files from staging
    # (步骤四：将 staging 中的原始未加密文件归档)
    step_4 = PythonOperator(
        task_id='archive_staging_data',
        python_callable=run_archive_original_data
    )

    # Task dependency chain (任务依赖顺序)
    step_1 >> step_2 >> step_3 >> step_4