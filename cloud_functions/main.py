import functions_framework
from google.cloud import bigquery
from google.cloud import storage
import os

# 当 GCS 有文件上传时，这个函数会被触发
@functions_framework.cloud_event
def process_file(cloud_event):
    data = cloud_event.data
    bucket_name = data["bucket"]
    file_name = data["name"] # 例如: project1/bank_data/123.csv

    # 如果传上来的不是 csv 文件，忽略
    if not file_name.endswith('.csv'):
        print(f"Skipping non-CSV file: {file_name}")
        return

    # ================= 必须修改这里 =================
    # 替换为你完整的 project-fe0250dd... ID
    project_id = "project-fe0250dd-e466-45c7-92d" 
    # ===============================================

    dataset_id = ""

    # 1. 路由逻辑：根据路径包含的文件夹名字，决定去哪个 Dataset
    if "bank_data/" in file_name:
        dataset_id = f"{project_id}.dj_project1_bank"
    elif "game_data/" in file_name:
        dataset_id = f"{project_id}.dj_project1_game"
    elif "healthcare_data/" in file_name:
        dataset_id = f"{project_id}.dj_project1_healthcare"
    else:
        print(f"文件 {file_name} 不在指定目录下，跳过处理。")
        return

    # 2. 提取表名：把 project1/bank_data/my_data.csv 变成 my_data
    base_name = os.path.basename(file_name) 
    table_name = os.path.splitext(base_name)[0] 
    table_id = f"{dataset_id}.{table_name}" 

    # 3. 把数据 Load 到 BigQuery
    bq_client = bigquery.Client(project=project_id)
    uri = f"gs://{bucket_name}/{file_name}"
    
    job_config = bigquery.LoadJobConfig(
        autodetect=True, # 让 BQ 自动识别 Schema
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1, # 跳过表头
    )

    print(f"开始将 {uri} 的数据灌入 {table_id}...")
    try:
        load_job = bq_client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result() # 等待数据灌入完成
        print(f"成功！已将 {load_job.output_rows} 行数据写入 {table_id}。")
    except Exception as e:
        print(f"导入 BigQuery 失败，中止后续删除操作。错误信息: {e}")
        return

    # 4. 彻底删除：BigQuery 加载成功后，直接干掉 GCS 里的原文件
    storage_client = storage.Client()
    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(file_name)
    
    print(f"正在从 GCS 彻底删除原文件: {file_name}")
    try:
        source_blob.delete()
        print("GCS 文件已成功删除，流程圆满结束！")
    except Exception as e:
        print(f"BigQuery 写入成功，但删除 GCS 文件失败: {e}")
