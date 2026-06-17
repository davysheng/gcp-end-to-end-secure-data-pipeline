import os
import shutil
import logging
from dotenv import load_dotenv

# Auto-load environment variables (自动加载环境变量)
load_dotenv()

# Configure logging (配置日志记录器)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Read directories from environment variables (从环境变量读取路径)
STAGING_DIR = os.environ.get(
    "GAME_STAGING_DIR",
    "./data/1_staging/game_staging"
)
ARCHIVE_DIR = os.environ.get(
    "GAME_ARCHIVE_DIR",
    "./data/1_archive/game_archive"
)


def archive_original_data() -> int:
    """
    Moves original unencrypted CSV files from game_staging to game_archive.
    (将 game_staging 中的原始未加密 CSV 文件移动到 game_archive)

    Returns:
        int: Number of files successfully archived. (成功归档的文件数量)
    """
    try:
        # Ensure archive directory exists (确保归档文件夹存在)
        os.makedirs(ARCHIVE_DIR, exist_ok=True)

        # Validate staging directory exists (验证 staging 目录存在)
        if not os.path.exists(STAGING_DIR):
            logger.error(f"Staging directory not found (找不到暂存目录): {STAGING_DIR}")
            raise FileNotFoundError(f"Staging directory not found: {STAGING_DIR}")

        # Filter valid CSV files only (只处理有效的 CSV 文件，过滤隐藏文件)
        valid_files = [
            f for f in os.listdir(STAGING_DIR)
            if f.endswith('.csv') and not f.startswith('.')
        ]

        if not valid_files:
            logger.info("No files found in game_staging, nothing to archive (game_staging 为空，无需归档)")
            return 0

        logger.info(f"Found {len(valid_files)} file(s) to archive (发现 {len(valid_files)} 个文件待归档)")

        moved_count = 0
        for file_name in valid_files:
            src_path = os.path.join(STAGING_DIR, file_name)
            dest_path = os.path.join(ARCHIVE_DIR, file_name)

            try:
                # Move file atomically from staging to archive (原子性移动文件到归档目录)
                shutil.move(src_path, dest_path)
                logger.info(f"Archived (已归档): {file_name} → game_archive/")
                moved_count += 1

            except OSError as e:
                # Handle individual file move errors (处理单个文件移动错误，记录后继续处理其他文件)
                logger.error(f"Failed to archive file (归档文件失败) {file_name}: {e}")
                continue

        logger.info(f"Archive complete. {moved_count} file(s) archived successfully (归档完成，共归档 {moved_count} 个文件)")
        return moved_count

    except Exception as e:
        logger.error(f"Unexpected error during archiving (归档过程中发生意外错误): {e}")
        raise


if __name__ == "__main__":
    archive_original_data()