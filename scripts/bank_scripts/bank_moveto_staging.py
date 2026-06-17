import os
import shutil
import logging
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

# Read directories from environment variables (从环境变量读取源路径和目标路径)
LANDING_DIR = os.environ.get(
    "BANK_LANDING_DIR",
    "./data/1_landing/bank_landing"
)
STAGING_DIR = os.environ.get(
    "BANK_STAGING_DIR",
    "./data/1_staging/bank_staging"
)


def transfer_landing_to_staging() -> int:
    """
    Moves all valid CSV files from bank_landing to bank_staging.
    (将 bank_landing 中的所有有效 CSV 文件移动到 bank_staging)

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

        # Filter out hidden files and non-CSV files (过滤隐藏文件和非 CSV 文件)
        valid_files = [
            f for f in files
            if f.endswith('.csv') and not f.startswith('.')
        ]

        if not valid_files:
            logger.info("No files found in bank_landing, nothing to transfer (bank_landing 为空，无需转移)")
            return 0

        logger.info(f"Found {len(valid_files)} file(s) to transfer (发现 {len(valid_files)} 个文件待转移)")

        moved_count = 0
        for file_name in valid_files:
            src_path = os.path.join(LANDING_DIR, file_name)
            dest_path = os.path.join(STAGING_DIR, file_name)

            try:
                # Move file atomically from landing to staging (原子性移动文件)
                shutil.move(src_path, dest_path)
                logger.info(f"Moved (已移动): {file_name} → bank_staging/")
                moved_count += 1

            except OSError as e:
                # Log individual file errors and continue with remaining files
                # (记录单个文件错误，继续处理其余文件)
                logger.error(f"Failed to move file (移动文件失败) {file_name}: {e}")
                continue

        logger.info(f"Transfer complete. {moved_count} file(s) moved successfully (转移完成，共移动 {moved_count} 个文件)")
        return moved_count

    except Exception as e:
        logger.error(f"Unexpected error during file transfer (文件转移时发生意外错误): {e}")
        raise


if __name__ == "__main__":
    transfer_landing_to_staging()