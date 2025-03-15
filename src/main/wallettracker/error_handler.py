import csv
import os
from datetime import datetime
from config import ERROR_LOG_FILE

# Ensure error log file exists
if not os.path.exists(ERROR_LOG_FILE):
    with open(ERROR_LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Timestamp', 'Error Type', 'Message', 'Details'])


async def log_error(error_type, message, details=""):
    """Log errors to CSV."""
    with open(ERROR_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), error_type, message, details])
