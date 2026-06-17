from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'davy',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Wrapper functions - import inside function for better isolation
# (包装函数 - 在函数内部 import，避免 DAG 加载失败)

def run_generate():
    """Generate mock game match logs (生成模拟游戏对局数据)"""
    from scripts.game_scripts_v2.game_generate_v2 import generate_daily_match_logs
    return generate_daily_match_logs()

def run_move_to_staging():
    """Move files from landing to staging (将文件从 landing 移动到 staging)"""
    from scripts.game_scripts_v2.game_moveto_staging_v2 import transfer_landing_to_staging
    return transfer_landing_to_staging()

def run_encrypt_and_upload():
    """Hash sensitive columns and upload to GCS (哈希敏感字段并上传至 GCS)"""
    from scripts.game_scripts_v2.game_upload_encrypted_gcs_v2 import encrypt_and_upload_to_gcs
    return encrypt_and_upload_to_gcs()

def run_archive():
    """Archive original unencrypted files (归档原始未加密文件)"""
    from scripts.game_scripts_v2.game_archive_v2 import archive_original_data
    return archive_original_data()


with DAG(
    dag_id='game_data_security_pipeline_v2',
    default_args=default_args,
    schedule='@daily',          # Run once per day (每天运行一次)
    catchup=False,              # Do not backfill missed runs (不补跑历史任务)
    max_active_runs=1,
    tags=['game', 'pipeline'],  # Tags for filtering in Airflow UI (用于 UI 筛选的标签)
) as dag:

    step_1 = PythonOperator(
        task_id='generate_landing_data',
        python_callable=run_generate,
    )

    step_2 = PythonOperator(
        task_id='move_data_to_staging',
        python_callable=run_move_to_staging,
    )

    step_3 = PythonOperator(
        task_id='encrypt_and_upload_to_gcs',
        python_callable=run_encrypt_and_upload,
    )

    step_4 = PythonOperator(
        task_id='archive_staging_data',
        python_callable=run_archive,
    )

    # Linear execution order - must run in sequence to prevent data loss
    # (线性执行顺序 - 必须按顺序执行，防止数据丢失)
    step_1 >> step_2 >> step_3 >> step_4