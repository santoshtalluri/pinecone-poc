import logging
import os
from flask import Flask
from config import Config
from utils import setup_logging
from routes import register_blueprints
from rag_utils_from_files import create_rag_system_from_files
import dotenv

# 📝 Set up logging first to capture all logs, even from imports
setup_logging(Config.LOG_FILE_PATH, Config.LOGGING_LEVEL)

# Initialize the Flask app
app = Flask(__name__)

# 🔥 Load environment variables from .env file
dotenv.load_dotenv()

# 🔥 Get environment variables for DATA_FOLDER and FAISS_INDEX_PATH
DATA_FOLDER = os.getenv('DATA_FOLDER', '/Users/santoshtalluri/Documents/MyDevProjects/MyProject/data')
FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', '/Users/santoshtalluri/Documents/MyDevProjects/MyProject/faiss_index')

# Register routes (Blueprints)
app = register_blueprints(app)

try:
    logging.info(f"🧠 Attempting to create RAG system from files in {DATA_FOLDER}...")
    vector_store, rag_system = create_rag_system_from_files(DATA_FOLDER, FAISS_INDEX_PATH)

    if vector_store is None:
        logging.error('❌ Vector store is None. Failed to initialize RAG system.')
        raise RuntimeError("Failed to create RAG system from files.")

except Exception as e:
    logging.error(f'❌ Error initializing RAG system: {str(e)}', exc_info=True)
    vector_store = None  # Explicitly set vector_store to None if an error occurs

if __name__ == "__main__":
    logging.info("📢 Starting Flask server...")
    try:
        app.run(host=Config.API_HOST, port=Config.API_PORT, debug=True)
    except Exception as e:
        logging.error(f'❌ Critical Error: Failed to start Flask server: {str(e)}', exc_info=True)