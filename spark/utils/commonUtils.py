import logging
import requests
from pathlib import Path

try:
    from project_utils.logger import get_logger
except ImportError:
    import sys
    from pathlib import Path as _Path

    sys.path.insert(0, str(_Path(__file__).resolve().parents[3]))
    from project_utils.logger import get_logger


def download_file(url, path):
    """Download the CSV dataset."""
    logger = get_logger(__name__)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading dataset from {url}")
    response = requests.get(url)
    response.raise_for_status()
    try:
        with open(path, "w") as f:
            f.write(response.text)
            logger.info(f"File downloaded successfully: {path}")
    except ValueError as e:
        logging.debug("Error while loading the file - {e}")
    return str(path)


def delete_file(file_name: str) -> bool:
    logger = get_logger(__name__)
    file_name = Path(file_name)
    logger.info(f"deleting file {file_name}")
    if file_name.exists() and file_name.is_file():
        file_name.unlink()
        logger.info(f"{file_name} deleted successfully")
    else:
        logger.info(f"{file_name} does not exist")
