from dotenv import load_dotenv
load_dotenv()

import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from config import Config
from rag_utils_from_files import create_rag_system_from_files

class VectorStoreInstance:
    """
    Singleton class for managing the FAISS vector store.
    
    This class initializes the FAISS vector store and ensures that 
    it is only created once. The vector store is used to manage 
    and retrieve RAG (Retrieval Augmented Generation) data.

    Attributes:
        _instance (FAISS): The single instance of the FAISS vector store.
    """
    _instance = None

    def __new__(cls):
        """
        Create or retrieve the singleton instance of the FAISS vector store.
        
        If the FAISS index exists, it is loaded. If it does not exist, 
        the system creates a new RAG from files in the DATA_FOLDER.
        """
        if cls._instance is None:
            try:
                # Path to the folder where the base RAG FAISS index is stored
                base_rag_path = Config.FAISS_INDEX_PATH
                logging.info(f"📂 Ensuring base RAG path exists: {base_rag_path}")
                
                os.makedirs(base_rag_path, exist_ok=True)

                index_path = os.path.join(base_rag_path, 'index.faiss')

                if os.path.exists(index_path):
                    logging.info(f'🧠 Loading FAISS vector store from {index_path}...')
                    cls._instance = FAISS.load_local(
                        base_rag_path, 
                        embeddings=OpenAIEmbeddings(), 
                        allow_dangerous_deserialization=True
                    )
                else:
                    logging.info(f'📂 No FAISS index found. Building base RAG system from files in {Config.DATA_FOLDER}...')
                    cls._instance, _ = create_rag_system_from_files(Config.DATA_FOLDER, base_rag_path)
            except Exception as e:
                logging.error(f'❌ Failed to initialize FAISS vector store: {str(e)}', exc_info=True)
                cls._instance = None
        return cls._instance