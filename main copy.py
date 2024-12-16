import os
import logging
from flask import Flask
from dotenv import load_dotenv
from halo import Halo  # Spinner for visual feedback
from vector_store_instance import vector_store  # Import the vector store from vector_store_instance.py

# Load environment variables
load_dotenv(dotenv_path='/Users/santoshtalluri/Documents/MyDevProjects/rag_with_url_project/.env')

# Initialize the Flask app
app = Flask(__name__)

# Logging Configuration
logging.basicConfig(
    filename='logs/errors.log', 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import and register routes
from routes.ask_route import ask_blueprint
from routes.build_rag_route import build_rag_blueprint
from routes.status_route import status_blueprint

# Register Blueprints
app.register_blueprint(ask_blueprint, url_prefix='/ask')
app.register_blueprint(build_rag_blueprint, url_prefix='/build-rag')
app.register_blueprint(status_blueprint, url_prefix='/status')

# Log server start
logging.info("Starting Flask server on http://0.0.0.0:5001")
print("Starting Flask server on http://0.0.0.0:5001")

# Check if RAG is initialized
try:
    from rag_utils_from_files import create_rag_system_from_files
    DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data')

    # 🔥 Define path to FAISS index
    path_to_faiss_index = os.path.join(DATA_FOLDER, 'faiss_index')  # Correctly define the path to FAISS index

    with Halo(text='Building RAG system from files...', spinner='dots') as spinner:
        logging.info(f"Attempting to create RAG system from files in {DATA_FOLDER}...")
        print(f"📂 Checking for files in {DATA_FOLDER}...")

        # Use the path_to_faiss_index when creating or loading FAISS
        vector_store = create_rag_system_from_files(DATA_FOLDER, path_to_faiss_index)

        if vector_store is None:
            logging.error('❌ Vector store is None. Check if RAG system is properly initialized.')
            spinner.fail("⚠️ No files found in the data folder to build the RAG system.")
            print("⚠️ No files found in the data folder to build the RAG system.")
        else:
            spinner.succeed("✅ RAG system successfully initialized from files.")
            print("✅ RAG system successfully initialized from files.")
except Exception as e:
    logging.error(f'❌ Failed to initialize RAG system: {str(e)}')
    print(f'❌ Failed to initialize RAG system: {str(e)}')

def check_vector_store():
    """Check the number of vectors in the FAISS vector store."""
    try:
        if vector_store:
            num_vectors = vector_store.num_vectors()
            logging.info(f'🧠 Number of vectors in FAISS store: {num_vectors}')
        else:
            logging.error('❌ Vector store is None.')
    except Exception as e:
        logging.error(f'❌ Error checking FAISS vector store: {str(e)}')


@app.route('/')
def home():
    return 'RAG System is Running!'

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    folder_path = "./data"  # Path to the folder containing your files
    path_to_faiss_index = os.path.join(folder_path, 'faiss_index')
    rag_system = create_rag_system_from_files(folder_path, path_to_faiss_index)
    if rag_system:
        logging.info("🎉 RAG system is ready to use!")
    else:
        logging.error("🚨 Failed to create the RAG system.")