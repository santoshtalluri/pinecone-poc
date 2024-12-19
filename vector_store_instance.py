from dotenv import load_dotenv
load_dotenv()

import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from config import Config
from rag_utils_from_files import create_rag_system_from_files
import pinecone

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
                logging.info(f'🧠 Initializing Pinecone Vector Store...')
                embeddings = OpenAIEmbeddings()
                pinecone.init(api_key=os.getenv('PINECONE_API_KEY'))
                index_name = os.getenv('PINECONE_INDEX_NAME')

                if index_name not in pinecone.list_indexes():
                    pinecone.create_index(index_name, dimension=1536)
                
                index = pinecone.Index(index_name)
                cls._instance = Pinecone(index, embeddings)
                logging.info(f'✅ Connected to Pinecone index: {index_name}')
            except Exception as e:
                logging.error(f'❌ Error initializing Pinecone vector store: {str(e)}', exc_info=True)
                cls._instance = None
        return cls._instance
