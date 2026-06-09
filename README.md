# 🚀 GCP Enterprise Multi-Domain Data Pipelines

An enterprise-grade, event-driven data routing architecture built on Google Cloud Platform (GCP). This project orchestrates three distinct industry data streams (Banking, Gaming, and Healthcare), automating their extraction, secure upload, dynamically routed ingestion into specific BigQuery datasets, and storage optimization.

## 🏗 Architecture Overview

The pipeline leverages a highly scalable, serverless "Central Router" pattern on GCP, orchestrated locally.

1. **Multi-Source Orchestration**: Local scripts and Airflow DAGs generate and process mock data for three separate domains:
   - 🏦 **Banking** (Encrypted uploads, staging mechanisms)
   - 🎮 **Gaming** (v2 data generation, encrypted uploads)
   - 🏥 **Healthcare** (Data generation, staging to archive workflows)
2. **Unified Storage Ingestion**: Processed data from all three pipelines is uploaded to Google Cloud Storage (GCS).
3. **Event-Driven Trigger**: Any new file landing in the GCS bucket triggers Google Cloud Eventarc.
4. **Serverless Central Router**: Eventarc securely invokes a single Gen 2 Cloud Run Function.
5. **Dynamic Routing**: The Python-based Cloud Function acts as a router. It reads the payload, identifies the data domain based on the file metadata/path, and dynamically loads the data into its corresponding **BigQuery Dataset** (e.g., `bank_dataset`, `game_dataset`, `healthcare_dataset`).
6. **Garbage Collection**: Upon successful BigQuery insertion, the original files in GCS are automatically deleted to optimize cloud storage costs.

## 🛠 Tech Stack

* **Cloud Provider**: Google Cloud Platform (GCP)
* **Storage & Data Warehouse**: Google Cloud Storage (GCS), BigQuery
* **Compute & Events**: Cloud Run Functions (Gen 2), Eventarc
* **Language & Orchestration**: Python 3.x, Apache Airflow
* **Security & IAM**: Principle of Least Privilege enforcing `Cloud Run Invoker` roles (successfully mitigating 403 Forbidden errors without exposing public endpoints).

## 📁 Repository Structure

```text
gcp-end-to-end-data-pipeline/
├── airflow_dags/             
│   ├── bank_data_pipeline_dag.py        # 🏦 Banking data extraction & orchestration
│   ├── game_data_pipeline_dag_v2.py     # 🎮 Gaming data extraction & orchestration
│   └── healthcare_pipeline_dag.py       # 🏥 Healthcare data extraction & orchestration
├── cloud_functions/          
│   ├── main.py                          # The core "Central Router" logic
│   └── requirements.txt                 # Dependencies (functions-framework, google-cloud-*)
├── scripts/                  
│   ├── bank_scripts/                    # Banking data generation & upload scripts
│   ├── game_scripts_v2/                 # Gaming data pipeline scripts
│   └── healthcare_scripts/              # Healthcare data processing scripts
└── image/                               # Architecture diagrams (coming soon)
