# utils/logger.py
import logging
import os
import time

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "performance.log")

# Setup logger configuration
logger = logging.getLogger("MealGenieLogger")
logger.setLevel(logging.INFO)

# Create file handler
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def log_performance(activity: str, duration_sec: float, extra_info: str = ""):
    """Log performance metrics of a specific activity."""
    msg = f"Activity: {activity} | Duration: {duration_sec:.4f}s"
    if extra_info:
        msg += f" | Details: {extra_info}"
    logger.info(msg)

def log_error(activity: str, error_msg: str):
    """Log errors encountered during execution."""
    logger.error(f"Error in {activity} | Message: {error_msg}")
