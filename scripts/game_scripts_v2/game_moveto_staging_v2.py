import os
import shutil
import logging
from dotenv import load_dotenv
load_dotenv()  # Auto-load environment variables from .env file (自动从 .env 文件加载环境变量)

# Configure logging (配置日志记录器)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Read directories from environment variables (从环境变量读取源路径和目标路径)
LANDING_DIR = os.environ.get(
    "GAME_LANDING_DIR",
    "./data/1_landing/game_landing"
)
STAGING_DIR = os.environ.get(
    "GAME_STAGING_DIR",
    "./data/1_staging/game_staging"
)


def transfer_landing_to_staging() -> int:
    """
    Moves all valid files from game_landing to game_staging.
    (将 game_landing 中的所有有效文件移动到 game_staging)

    Returns:
        int: Number of files successfully moved. (成功移动的文件数量)
    """
    try:
        # Ensure staging directory exists (确保 staging 文件夹存在)
        os.makedirs(STAGING_DIR, exist_ok=True)

        # List all files in landing directory (读取 landing 文件夹中的所有文件)
        try:
            files = os.listdir(LANDING_DIR)
        except FileNotFoundError:
            logger.error(f"Landing directory not found (找不到源文件夹): {LANDING_DIR}")
            raise

        # Filter out hidden files and subdirectories (过滤隐藏文件和子文件夹，只处理真实文件)
        valid_files = [
            f for f in files
            if os.path.isfile(os.path.join(LANDING_DIR, f)) and not f.startswith('.')
        ]

        if not valid_files:
            logger.info("No files found in game_landing, nothing to transfer (game_landing 为空，无需转移)")
            return 0

        logger.info(f"Found {len(valid_files)} file(s) to transfer (发现 {len(valid_files)} 个文件待转移)")

        moved_count = 0
        for file_name in valid_files:
            src_path = os.path.join(LANDING_DIR, file_name)
            dest_path = os.path.join(STAGING_DIR, file_name)

            # Move file atomically from landing to staging (原子性移动文件)
            shutil.move(src_path, dest_path)
            logger.info(f"Moved (已移动): {file_name} → game_staging/")
            moved_count += 1

        logger.info(f"Transfer complete. {moved_count} file(s) moved successfully (转移完成，共移动 {moved_count} 个文件)")
        return moved_count

    except Exception as e:
        logger.error(f"Unexpected error during file transfer (文件转移时发生意外错误): {e}")
        raise


if __name__ == "__main__":
    transfer_landing_to_staging()