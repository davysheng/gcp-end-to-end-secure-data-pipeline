from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# 🌟 架构升级：不再需要引入笨重的 DockerOperator 和 Mount 了！

# 🌟 路径升级：全部指向我们刚刚改好的 game_scripts_v2 文件夹
from scripts.game_scripts_v2.generate_game_data_v2 import generate_daily_match_logs
from scripts.game_scripts_v2.gamedata_move_to_staging_v2 import transfer_landing_to_staging
from scripts.game_scripts_v2.gamedata_upload_encrypted_to_gcs_v2 import encrypt_and_upload_to_gcs
from scripts.game_scripts_v2.gamedata_archive_staging_v2 import archive_original_data

default_args = {
    'owner': 'davy',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# 名字顺便升个级，标记这是我们的 API 解耦版本
with DAG('GameData_Security_Pipeline_v2', default_args=default_args, schedule='*/10 * * * *', catchup=False) as dag:

    step_1 = PythonOperator(
        task_id='generate_landing_data',
        python_callable=generate_daily_match_logs
    )

    step_2 = PythonOperator(
        task_id='move_data_to_staging',
        python_callable=transfer_landing_to_staging
    )

    # 🚀 革命性升级：原本庞大的 DockerOperator，现在只是一个轻量级的 Python 脚本
    # 脚本内部会通过网络秒级调用后台长驻的加密 Docker API，处理完直接上云
    step_3 = PythonOperator(
        task_id='encrypt_and_upload_to_gcs',
        python_callable=encrypt_and_upload_to_gcs
    )

    step_4 = PythonOperator(
        task_id='archive_staging_data',
        python_callable=archive_original_data
    )

    # 🔗 完美的单线拓扑关系（必须按严格顺序执行，防止数据丢失）
    # 生成 -> 移动 -> [调API加密并上云] -> [确认上云成功后] 归档清理
    step_1 >> step_2 >> step_3 >> step_4