import os
import logging
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        content = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
        if not content.strip():
            logging.warning(f'⚠️ No text extracted from PDF {file_path}. It may be an image-based PDF.')
        return content
    except Exception as e:
        logging.error(f'❌ Error extracting text from PDF {file_path}: {str(e)}', exc_info=True)
        return ''

def create_rag_system_from_files(folder_path, path_to_faiss_index):
    """Create RAG system from multiple files in a folder."""
    try:
        # If the FAISS index already exists, load it
        if os.path.exists(path_to_faiss_index) and os.path.exists(os.path.join(path_to_faiss_index, 'index.faiss')):
            logging.info(f'🧠 Loading existing FAISS vector store from {path_to_faiss_index}...')
            vector_store = FAISS.load_local(path_to_faiss_index, embeddings=OpenAIEmbeddings(), allow_dangerous_deserialization=True)
        
        else:
            logging.info(f'📂 No existing FAISS store found. Creating a new RAG system from files in {folder_path}...')

            # Get all PDF and TXT files in the folder
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.pdf', '.txt'))]

            if not files:
                logging.warning(f'⚠️ No PDF or TXT files found in {folder_path} to create the RAG system.')
                return None, None

            documents = []
            for file_path in files:
                if file_path.endswith('.pdf'):
                    content = extract_text_from_pdf(file_path)
                elif file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                if content.strip():
                    logging.info(f'📄 Extracted content from {file_path} (first 100 chars): {content[:100]}...')
                    documents.append(Document(page_content=content, metadata={"source": file_path}))

            if not documents:
                logging.error(f'❌ No content extracted from files in {folder_path}. RAG system cannot be created.')
                return None, None

            # Create the FAISS vector store from the documents
            embeddings = OpenAIEmbeddings()
            vector_store = FAISS.from_documents(documents, embeddings)
            os.makedirs(path_to_faiss_index, exist_ok=True)  # Ensure the FAISS index path exists
            vector_store.save_local(path_to_faiss_index)

        retriever = vector_store.as_retriever()
        rag_system = RetrievalQA.from_chain_type(llm=ChatOpenAI(model="gpt-4-turbo"), retriever=retriever)
        
        logging.info(f'✅ RAG system created successfully with {vector_store.index.ntotal} vectors.')
        return vector_store, rag_system
    except Exception as e:
        logging.error(f'❌ Error creating RAG system from files: {str(e)}', exc_info=True)
        return None, None