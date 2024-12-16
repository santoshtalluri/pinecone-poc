import os

class Config:
    """Global Configuration Class"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_FOLDER = os.getenv('DATA_FOLDER', os.path.join(BASE_DIR, 'data'))
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', os.path.join(BASE_DIR, 'faiss_index'))
    FAISS_NEW_RAGS_PATH = os.path.join(FAISS_INDEX_PATH, 'new_rags')  # New RAGs created under this path
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', os.path.join(BASE_DIR, 'logs/errors.log'))
    LOGGING_LEVEL = 'INFO'
    API_PORT = 5001
    API_HOST = '0.0.0.0'