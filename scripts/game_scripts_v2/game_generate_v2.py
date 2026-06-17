import os
import csv
import uuid
import random
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()  # Auto-load environment variables from .env file (自动从 .env 文件加载环境变量)

# Configure logging (配置日志记录器)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Read target directory from environment variable (从环境变量读取目标路径)
# Falls back to a relative path for local development (本地开发时使用相对路径作为默认值)
TARGET_DIR = os.environ.get(
    "GAME_LANDING_DIR",
    "./data/1_landing/game_landing"
)

def generate_daily_match_logs() -> str:
    """
    Generates mock daily game match logs and saves them as a CSV file.
    (生成模拟的每日游戏对局日志并保存为 CSV 文件)

    Returns:
        str: The file path of the generated CSV file.
             (返回生成的 CSV 文件路径)
    """
    try:
        # Ensure the landing directory exists (确保落地文件夹存在，不存在则自动创建)
        os.makedirs(TARGET_DIR, exist_ok=True)

        # Generate a unique filename using current timestamp (用当前时间戳生成唯一文件名，精确到秒)
        file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"game_logs_{file_timestamp}.csv"
        file_path = os.path.join(TARGET_DIR, file_name)

        # Define CSV headers - fact table structure (定义字段头 - 事实表结构)
        headers = [
            "match_id",            # Unique match identifier (唯一对局ID)
            "player_id",           # Player identifier (玩家ID)
            "damage_dealt",        # Total damage dealt in match (对局总伤害)
            "match_duration_secs", # Match duration in seconds (对局时长，单位秒)
            "match_timestamp"      # Event timestamp for partitioning (事件时间戳，用于分区)
        ]

        # Generate between 900 to 1100 match log rows (随机生成900到1100条对局记录)
        num_rows = random.randint(900, 1100)

        # Calculate today's start time for realistic timestamp generation
        # (计算今天00:00，用于生成合理的对局时间戳)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        seconds_since_midnight = int((datetime.now() - today_start).total_seconds())

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            for _ in range(num_rows):
                match_id = str(uuid.uuid4())

                # Player pool of 50,000 players for realistic distribution
                # (5万玩家池，更接近真实分布)
                player_id = f"P{random.randint(10000, 60000)}"

                # Skewed damage distribution using Gaussian model
                # (使用高斯分布模拟真实伤害数据：大多数玩家造成中等伤害)
                damage_dealt = int(random.gauss(mu=8000, sigma=3000))
                damage_dealt = max(800, min(damage_dealt, 18500))

                match_duration_secs = random.randint(900, 2400)

                # Generate match time within today's range only
                # (只在今天00:00到当前时刻之间生成对局时间，避免跨天数据重叠)
                random_seconds = random.randint(0, max(seconds_since_midnight, 1))
                match_time = (
                    today_start + timedelta(seconds=random_seconds)
                ).strftime("%Y-%m-%d %H:%M:%S")

                writer.writerow([
                    match_id,
                    player_id,
                    damage_dealt,
                    match_duration_secs,
                    match_time
                ])

        logger.info("Successfully generated game match log file (成功生成游戏对局日志文件)")
        logger.info(f"File path (文件路径): {file_path}")
        logger.info(f"Fields (字段): {headers}")
        logger.info(f"Total rows generated (生成行数): {num_rows}")

        return file_path

    except OSError as e:
        logger.error(f"File system error while generating game data (文件系统错误): {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during game data generation (数据生成时发生意外错误): {e}")
        raise


if __name__ == "__main__":
    generate_daily_match_logs()