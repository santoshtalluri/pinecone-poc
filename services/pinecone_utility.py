import os
import logging
from pinecone import Pinecone, ServerlessSpec  # Import updated Pinecone API
from flask import Flask, request, jsonify
from langchain_community.embeddings import OpenAIEmbeddings  # Corrected import
from dotenv import load_dotenv
from halo import Halo  # For spinner animations
from routes import register_blueprints

# ============================
# 🔥 Load Environment Variables 🔥
# ============================
load_dotenv()

# Environment Variables
DATA_FOLDER = os.getenv('DATA_FOLDER', './data')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'rag-index')

# ============================
# 🔥 Logging Configuration 🔥
# ============================
logs_path = os.path.join(os.getcwd(), 'logs')
os.makedirs(logs_path, exist_ok=True)  # Ensure logs directory exists
logging.basicConfig(
    filename=os.path.join(logs_path, 'errors.log'), 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ============================
# 🔥 Initialize Flask App 🔥
# ============================
app = Flask(__name__)
# Register routes (Blueprints)
app = register_blueprints(app)

# ============================
# 🔥 Initialize Pinecone 🔥
# ============================
try:
    # Create Pinecone instance using API key
    pc = Pinecone(api_key=PINECONE_API_KEY)  # New Pinecone instance approach
    
    # Check if the index exists, if not, create it
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        logging.info(f"📢 Index {PINECONE_INDEX_NAME} not found. Creating it now...")
        pc.create_index(
            name=PINECONE_INDEX_NAME, 
            dimension=1536, 
            metric='cosine', 
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-east-1'  # Corrected the region based on your logs
            )
        )
    
    # Connect to the Pinecone index
    index = pc.Index(PINECONE_INDEX_NAME)  # ✅ Corrected method for getting the index
    logging.info(f'✅ Successfully connected to Pinecone index: {PINECONE_INDEX_NAME}')
except Exception as e:
    logging.error(f'❌ Failed to connect to Pinecone: {str(e)}', exc_info=True)
    index = None

# ============================
# 🔥 Run the Application 🔥
# ============================
if __name__ == "__main__":
    logging.info("🚀 Starting RAG system initialization")
    app.run(host='0.0.0.0', port=5001)