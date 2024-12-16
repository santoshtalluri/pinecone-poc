import os

class Config:
    """Global Configuration Class"""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOCAL_STORAGE = True  # Use local storage for vector store
    DATA_FOLDER = os.getenv('DATA_FOLDER', os.path.join(BASE_DIR, 'data'))  # Fallback to default
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', os.path.join(BASE_DIR, 'faiss_index'))
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', os.path.join(BASE_DIR, 'logs/errors.log'))

    # Ensure FAISS index path exists
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)

    # API Configurations
    API_PORT = int(os.getenv('API_PORT', 5001))
    API_HOST = os.getenv('API_HOST', '0.0.0.0')