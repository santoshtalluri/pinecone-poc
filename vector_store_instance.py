from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env

import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from config import Config
from rag_utils_from_files import create_rag_system_from_files

class VectorStoreInstance:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                # Ensure faiss_index folder exists
                os.makedirs(Config.FAISS_INDEX_PATH, exist_ok=True)  # ✅ Create folder if not present

                index_path = os.path.join(Config.FAISS_INDEX_PATH, 'index.faiss')

                # Check if the FAISS index file exists
                if os.path.exists(index_path):
                    logging.info(f'🧠 Loading FAISS vector store from {index_path}...')
                    cls._instance = FAISS.load_local(
                        Config.FAISS_INDEX_PATH, 
                        OpenAIEmbeddings(), 
                        allow_dangerous_deserialization=True  # Allow FAISS file deserialization
                    )
                    logging.info(f'✅ Loaded FAISS vector store with {cls._instance.index.ntotal} vectors.')
                else:
                    logging.info(f'📂 No FAISS store found. Building RAG system from files in {Config.DATA_FOLDER}...')
                    cls._instance, _ = create_rag_system_from_files(Config.DATA_FOLDER, Config.FAISS_INDEX_PATH)  # This will create the FAISS index
                    logging.info(f'✅ RAG system created successfully and saved in {Config.FAISS_INDEX_PATH}')
                    
            except Exception as e:
                logging.error(f'❌ Failed to initialize FAISS vector store: {str(e)}', exc_info=True)
                cls._instance = None  # Ensure instance is None if there's an error
        return cls._instance

# Singleton access point
vector_store = VectorStoreInstance()

if vector_store is None:
    logging.critical("🚨 Failed to initialize FAISS vector store. Exiting application.")
    raise SystemExit("🚨 Failed to initialize FAISS vector store. Exiting application.")