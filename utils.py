import os
import logging

def ensure_directory_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logging.info(f'📁 Created directory: {path}')

def get_logging_level(log_level_str):
    levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    return levels.get(log_level_str.upper(), logging.INFO)

def setup_logging(log_file_path, log_level):
    ensure_directory_exists(os.path.dirname(log_file_path))
    log_level = get_logging_level(log_level)
    
    logging.basicConfig(
        filename=log_file_path,
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        force=True  # Ensure other modules don't reset logging
    )

    # Add console output for logs
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    
    # Attach the console handler to the root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    
    logging.info(f'✅ Logging initialized at level: {log_level}, log file: {log_file_path}')