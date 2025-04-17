import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name):
    """Creates and returns a logger with rotating file handler."""

    # Get path to LOCALAPPDATA
    local_appdata = os.getenv("LOCALAPPDATA")
    log_dir = os.path.join(local_appdata, "pyRTQA", "logs")

    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Full path for the log file
    log_file_path = os.path.join(log_dir, "pyrtqa.log")

    # Setup logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed logs

    # Rotating file handler (5 files, 1MB each)
    handler = RotatingFileHandler(log_file_path, maxBytes=1 * 1024 * 1024, backupCount=5)
    handler.setLevel(logging.DEBUG)

    # Define log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# Example usage
if __name__ == "__main__":
    log = setup_logger("PyRTQA")
    log.info("Logger is set up and running!")
