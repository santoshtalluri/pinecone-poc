import os
import logging
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from config import Config
from rag_utils_from_files import create_rag_system_from_files  # Ensure this is imported

# Load environment variables
load_dotenv(dotenv_path='/Users/santoshtalluri/Documents/MyDevProjects/MyProject/.env')

# Logging Configuration
logging.basicConfig(
    filename=Config.LOG_FILE_PATH, 
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class VectorStoreInstance:
    """Singleton Class to create and manage the FAISS vector store."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                faiss_index_path = Config.FAISS_INDEX_PATH
                if os.path.exists(faiss_index_path):
                    logging.info(f'🧠 Attempting to load FAISS vector store from {faiss_index_path}...')
                    try:
                        cls._instance = FAISS.load_local(faiss_index_path, embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)
                        logging.info(f'✅ Successfully loaded FAISS vector store with {cls._instance.index.ntotal} vectors.')
                    except Exception as e:
                        logging.error(f'❌ Failed to load FAISS index, attempting to create a new one: {str(e)}')
                        cls._instance = cls._create_new_vector_store(faiss_index_path)
                else:
                    logging.warning(f'⚠️ FAISS index path does not exist. Creating new FAISS vector store at {faiss_index_path}...')
                    os.makedirs(faiss_index_path, exist_ok=True)
                    cls._instance = cls._create_new_vector_store(faiss_index_path)
            except Exception as e:
                logging.error(f'❌ Critical Error: Failed to initialize FAISS vector store: {str(e)}', exc_info=True)
        return cls._instance

    @staticmethod
    def _create_new_vector_store(faiss_index_path):
        """Create a new FAISS vector store from files in the data folder."""
        try:
            data_folder = Config.DATA_FOLDER
            logging.info(f'📂 Attempting to create new FAISS vector store from files in {data_folder}...')
            vector_store, rag_system = create_rag_system_from_files(data_folder, faiss_index_path)
            if vector_store is not None:
                logging.info(f'✅ New FAISS vector store created successfully with {vector_store.index.ntotal} vectors.')
            else:
                logging.error(f'❌ Failed to create FAISS vector store. No files found in {data_folder}.')
            return vector_store
        except Exception as e:
            logging.error(f'❌ Error creating FAISS vector store: {str(e)}', exc_info=True)
            return None


vector_store = VectorStoreInstance()

rag_system = None

try:
    if vector_store:
        retriever = vector_store.as_retriever()
        rag_system = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4-turbo", temperature=0.7), 
            retriever=retriever
        )
        logging.info(f'✅ RAG system successfully initialized with {vector_store.index.ntotal} vectors.')
    else:
        logging.error('❌ Failed to initialize RAG system because vector_store is None.')
except Exception as e:
    logging.error(f'❌ Critical Error: Failed to initialize RAG system: {str(e)}', exc_info=True)