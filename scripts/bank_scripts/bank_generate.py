import os
import csv
import uuid
import random
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

# Load base config (.env with Docker container paths)
# (先加载基础配置，包含 Docker 容器路径)
load_dotenv(find_dotenv())

# Override with local config if it exists (.env.local with Mac absolute paths)
# (如果本地配置文件存在，用 Mac 绝对路径覆盖，供本地测试使用)
local_env = find_dotenv('.env.local')
if local_env:
    load_dotenv(local_env, override=True)

# Configure logging (配置日志记录器)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Read target directory from environment variable (从环境变量读取目标落地路径)
# Falls back to a relative path for local development (本地开发时使用相对路径作为默认值)
TARGET_DIR = os.environ.get(
    "BANK_LANDING_DIR",
    "./data/1_landing/bank_landing"
)


def generate_daily_bank_customers() -> str:
    """
    Generates a daily SCD Type 2 snapshot of mock bank customer dimension records
    and saves them as a CSV file.
    (生成每日银行客户维度表的 SCD Type 2 状态快照，并保存为 CSV 文件)

    SCD Type 2 (Slowly Changing Dimension Type 2 / 缓慢变化维度拉链表):
    Each row represents one version of a customer's state, tracked by
    start_date and end_date. Active records use end_date = '9999-12-31'.
    (每行代表客户状态的一个版本，通过 start_date 和 end_date 追踪历史变化。
    当前有效记录的 end_date 为 '9999-12-31')

    Returns:
        str: The file path of the generated CSV file. (返回生成的 CSV 文件路径)
    """
    try:
        # Ensure the landing directory exists (确保落地文件夹存在，不存在则自动创建)
        os.makedirs(TARGET_DIR, exist_ok=True)

        # Generate a unique filename using current timestamp, no microseconds
        # (用当前时间戳生成唯一文件名，精确到秒，去掉微秒)
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"bank_customers_{file_timestamp}.csv"
        file_path = os.path.join(TARGET_DIR, file_name)

        # Define CSV headers - SCD Type 2 dimension table structure
        # (定义字段头 - SCD Type 2 维度表结构)
        headers = [
            "customer_id",   # Unique customer identifier (唯一客户ID)
            "account_tier",  # Customer tier: Standard, Gold, Platinum (账户等级)
            "risk_level",    # Risk classification (风险等级)
            "credit_score",  # Credit score between 300-850 (信用评分)
            "start_date",    # Date this version of the record became active (记录生效日期)
            "end_date"       # Date this version expires; '9999-12-31' = currently active
                             # (记录失效日期；'9999-12-31' 表示当前有效记录)
        ]

        # Generate between 900 to 1100 customer state snapshot rows
        # (随机生成 900 到 1100 条客户状态快照记录)
        num_rows = random.randint(900, 1100)

        # Sentinel end date for currently active SCD2 records
        # (SCD2 拉链表中表示"当前有效"的哨兵结束日期)
        active_end_date = "9999-12-31"

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for _ in range(num_rows):
                # Generate unique customer ID using full UUID to eliminate collision risk
                # (使用完整 UUID 生成唯一客户ID，消除截断 UUID 导致碰撞的风险)
                customer_id = f"CUST-{str(uuid.uuid4()).upper()}"

                # Account tier distribution (账户等级分布)
                account_tier = random.choice(["Standard", "Gold", "Platinum"])

                # Risk level with realistic skew: low risk is most common
                # (风险等级加权分布：低风险客户占多数，更接近真实业务场景)
                risk_level = random.choices(
                    ["Low", "Medium", "High"],
                    weights=[70, 20, 10],
                    k=1
                )[0]

                # Credit score range (信用评分范围)
                credit_score = random.randint(300, 850)

                # Start date: random day within the past year
                # (生效日期：过去一年内随机选择一天，模拟客户状态变更的历史分布)
                random_days_ago = random.randint(1, 365)
                start_date = (
                    datetime.now() - timedelta(days=random_days_ago)
                ).strftime("%Y-%m-%d")

                writer.writerow([
                    customer_id,
                    account_tier,
                    risk_level,
                    credit_score,
                    start_date,
                    active_end_date
                ])

        logger.info("Successfully generated bank customer snapshot file (成功生成银行客户快照文件)")
        logger.info(f"File path (文件路径): {file_path}")
        logger.info(f"Fields (字段): {headers}")
        logger.info(f"Total rows generated (生成行数): {num_rows}")

        return file_path

    except OSError as e:
        logger.error(f"File system error while generating bank data (文件系统错误): {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during bank data generation (数据生成时发生意外错误): {e}")
        raise


if __name__ == "__main__":
    generate_daily_bank_customers()