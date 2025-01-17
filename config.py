import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

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

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "my-resume4")

    PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")

    PINECONE_INDEX_DIMENSION = 1024  # Update to match your Pinecone index dimension

    EMBEDDING_MODEL = "openai"  # Options: "openai", "bert", "fasttext", "mpnet", "instructor-xl"
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    OLLAMA_EMBEDDING_MODEL = "mxbai-embed-large"  # Add this new config
    #OPENAI_EMBEDDING_DIMENSIONS = 3072  # Example dimension for OpenAI
    #OLLAMA_EMBEDDING_DIMENSIONS = 1042  # Example dimension for Ollama

    # Supported embedding models
    EMBEDDING_MODEL = "openai"  # Current embedding model
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    OLLAMA_EMBEDDING_MODEL = "mxbai-embed-large"
    FASTTEXT_MODEL_PATH = os.getenv('FASTTEXT_MODEL_PATH', os.path.join(BASE_DIR, 'cc.en.300.bin'))


    @staticmethod
    def get_index_dimensions():
        """Determine the index dimensions based on the embedding model."""
        if Config.EMBEDDING_MODEL == "openai" and Config.OPENAI_EMBEDDING_MODEL == "text-embedding-3-large":
            return 3072
        elif Config.EMBEDDING_MODEL == "ollama" and Config.OLLAMA_EMBEDDING_MODEL == "mxbai-embed-large":
            return 1042
        else:
            raise ValueError(f"Unsupported embedding model configuration: {Config.EMBEDDING_MODEL}")

    @staticmethod
    def get_embedding_config():
        """
        Returns the embedding model configuration based on the EMBEDDING_MODEL attribute.
        """
        if Config.EMBEDDING_MODEL == "openai":
            return {
                "model_name": Config.OPENAI_EMBEDDING_MODEL,
                "dimensions": 3072,  # Example dimension for OpenAI text-embedding-3-large
            }
        elif Config.EMBEDDING_MODEL == "ollama":
            return {
                "model_name": Config.OLLAMA_EMBEDDING_MODEL,
                "dimensions": 1042,  # Example dimension for mxbai-embed-large
            }
        elif Config.EMBEDDING_MODEL == "fasttext":
            return {
                "model_path": Config.FASTTEXT_MODEL_PATH,
                "dimensions": 300,  # FastText typically uses 300 dimensions
            }
        else:
            raise ValueError(f"Unsupported embedding model: {Config.EMBEDDING_MODEL}")
            
    # Add INSTRUCTOR_MODEL_PATH
    INSTRUCTOR_MODEL_PATH = os.getenv(
        'INSTRUCTOR_MODEL_PATH',
        os.path.join(BASE_DIR, 'models/hkunlp/instructor-xl')
    )

    # ================================
    # OpenAI Embedding Model Configuration
    # ================================

    # Specify the embedding model name
    # Example: "text-embedding-3-large" for OpenAI's advanced embedding model
    # You can also switch to other models (e.g., "text-embedding-ada-002").
    

    # Specify the desired dimensions for the embedding model.
    # Ensure this value matches your Pinecone or FAISS index dimensions.
    # If left as None, the model will use its default dimensions (e.g., 1536 for text-embedding-3-large).
    # Set to 1024 for compatibility with existing indices expecting 1024-dimensional vectors.
    #OPENAI_EMBEDDING_DIMENSIONS = 1024  # Adjust this to match your vector index

    # Ollama Configuration
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://127.0.0.1:11434')  # Default to local Ollama service
    
    OLLAMA_GENERATION_MODEL = "llama2"  # Model capable of text generation

    LLM_MODEL = "ollama"  # Options: "openai" for ChatGPT or "ollama" for local Ollama
    
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