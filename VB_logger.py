import logging
import sys
import time
from pathlib import Path


def _init_logging(session_datetime: str):
    log_folder = Path.cwd() / "logs"
    log_file = f"log_{session_datetime}.log"
    log_folder.mkdir(parents=True, exist_ok=True)
    log_file_path = log_folder.joinpath(log_file)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s - %(asctime)s - %(name)s - %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout),
        ],
    )
    # logger = logging.getLogger(__name__)
    # handler = logging.StreamHandler(sys.stdout)
    # logger.addHandler(handler)


if __name__ == "__main__":
    session_datetime = time.strftime("%Y%m%d_%H%M%S")
    _init_logging(session_datetime)
    logger = logging.getLogger(__name__)
    logger.info("test")
