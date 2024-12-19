import os

class Config:
    """Global Configuration Class
    
    This class contains all the configurable paths, file locations, and system settings
    for the RAG project. All paths are dynamically created relative to the project's 
    base directory unless overridden by environment variables.

    Attributes:
        BASE_DIR (str): The base directory of the project.
        DATA_FOLDER (str): The folder where input PDF and TXT files are stored for RAG creation.
        FAISS_INDEX_PATH (str): The directory where the FAISS index files are stored for the base RAG.
        FAISS_NEW_RAGS_PATH (str): The directory where new RAGs created by the API are stored.
        LOG_FILE_PATH (str): Path to the log file where error and info logs are written.
        LOGGING_LEVEL (str): The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        API_PORT (int): The port on which the Flask API server runs.
        API_HOST (str): The host IP on which the Flask API server runs.
        PINECONE_API_KEY (str): API key for Pinecone.
        PINECONE_INDEX_NAME (str): Name of the Pinecone index.
        FASTTEXT_HOME (str): The directory where FastText models are stored.
        FASTTEXT_MODEL_PATH (str): The path to the FastText model file.
    """

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Path of the directory where the project is located
    
    DATA_FOLDER = os.getenv('DATA_FOLDER', os.path.join(BASE_DIR, 'data'))  # Path to the folder containing input files (PDF, TXT)
    
    FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', os.path.join(BASE_DIR, 'faiss_index'))  # Path to the folder where the FAISS index is stored
    
    FAISS_NEW_RAGS_PATH = os.path.join(FAISS_INDEX_PATH, 'new_rags')  # Path to the folder where newly created RAGs are stored
    
    LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', os.path.join(BASE_DIR, 'logs/errors.log'))  # Path to the log file
    
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    API_PORT = int(os.getenv('API_PORT', 5001))  # Port on which the Flask API server runs
    
    API_HOST = os.getenv('API_HOST', '0.0.0.0')  # Host IP for the Flask server

    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
    
    PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')

    EMBEDDING_MODEL = "instructor-xl"  # Options: "openai", "bert", "fasttext", "mpnet", "instructor-xl"
    
    # ✅ NEW: FastText Configuration
    #HOME_DIRECTORY = os.path.expanduser('~')  # This will point to /Users/username or /home/username
    # Use project-level directory for FastText
    FASTTEXT_HOME = os.getenv('FASTTEXT_HOME', os.path.join(BASE_DIR, '.fasttext'))  # Updated to use project directory
    FASTTEXT_MODEL_PATH = os.getenv('FASTTEXT_MODEL_PATH', os.path.join(FASTTEXT_HOME, 'cc.en.300.bin'))  # Path to FastText model

    import logging

    logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )