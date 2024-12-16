import os
import logging
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from PyPDF2 import PdfReader

load_dotenv()
FAISS_INDEX_BASE_PATH = os.getenv('FAISS_INDEX_PATH')

DATA_FOLDER = os.getenv('DATA_FOLDER')
path_to_faiss_index = os.getenv('FAISS_INDEX_PATH')

vector_store = None
rag_system = None

class VectorStoreInstance:
    """Singleton Class to create and manage the FAISS vector store."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            try:
                startup_rag_path = os.path.join(FAISS_INDEX_BASE_PATH, 'system_startup')
                if os.path.exists(startup_rag_path):
                    logging.info(f'🧠 Loading startup RAG from {startup_rag_path}...')
                    cls._instance = FAISS.load_local(startup_rag_path, embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)
                    logging.info(f'✅ Loaded FAISS vector store with {cls._instance.index.ntotal} vectors.')
                else:
                    logging.info(f'📂 No RAG store found. Building system startup RAG from files in {os.getenv("DATA_FOLDER")}...')
                    cls._instance = create_rag_from_single_file(os.getenv("DATA_FOLDER"), startup_rag_path, is_new=True)
            except Exception as e:
                logging.error(f'❌ Failed to initialize RAG system: {str(e)}', exc_info=True)
        return cls._instance

try:
    if os.path.exists(path_to_faiss_index):
        logging.info(f'🧠 Loading FAISS vector store from {path_to_faiss_index}...')
        vector_store = FAISS.load_local(path_to_faiss_index, embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        logging.info(f'🧠 Vector store loaded successfully.')
    else:
        files = [os.path.join(DATA_FOLDER, f) for f in os.listdir(DATA_FOLDER) if f.lower().endswith(('.pdf', '.txt'))]
        documents = []
        for file_path in files:
            if file_path.endswith('.pdf'):
                reader = PdfReader(file_path)
                content = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
            if content.strip():
                documents.append(Document(page_content=content, metadata={"source": file_path}))
        vector_store = FAISS.from_documents(documents, OpenAIEmbeddings())
        vector_store.save_local(path_to_faiss_index)

    retriever = vector_store.as_retriever()
    rag_system = RetrievalQA.from_chain_type(llm=ChatOpenAI(model="gpt-4-turbo"), retriever=retriever)
    logging.info(f'✅ RAG system successfully initialized with {vector_store.index.ntotal} vectors.')
except Exception as e:
    logging.error(f'❌ Error initializing FAISS vector store: {str(e)}', exc_info=True)