import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Import extract_text_from_pdf from the new utility file
from utilities.pdf_extraction_utility import extract_text_from_pdf,extract_text_from_pdf_url,extract_text_from_url,extract_text_from_webpage

# Import configuration settings from Config
from config import Config

def read_file_content(file_path):
    """Read the content of a file (PDF or TXT)"""
    try:
        if file_path.endswith('.pdf'):
            return extract_text_from_pdf(file_path)
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        else:
            logging.warning(f'⚠️ Unsupported file format for {file_path}. Skipping.')
            return ''
    except Exception as e:
        logging.error(f'❌ Error reading file {file_path}: {str(e)}', exc_info=True)
        return ''

def create_rag_system_from_files(folder_path, path_to_faiss_index):
    """
    Create the RAG system from files in a folder.
    If `folder_path` is a file, treat it as a single file.
    """
    try:
        if os.path.isfile(folder_path):
            logging.info(f"📁 Detected single file path. Converting to list of files: {folder_path}")
            files = [folder_path]
        else:
            logging.info(f"📂 Processing directory: {folder_path}")
            files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.pdf', '.txt'))]

        if not files:
            logging.warning(f'⚠️ No documents found in {folder_path} to create the RAG system.')
            return None, None

        documents = []
        for file_path in files:
            content = ''
            if file_path.endswith('.pdf'):
                content = extract_text_from_pdf(file_path)
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

            if content.strip():
                documents.append(Document(page_content=content, metadata={"source": file_path}))

        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(documents, embeddings)

        # ✅ Ensure FAISS path exists
        os.makedirs(path_to_faiss_index, exist_ok=True)
        
        vector_store.save_local(path_to_faiss_index)  # Save the FAISS index to disk
        logging.info(f'✅ RAG system created successfully with {vector_store.index.ntotal} vectors.')
        return vector_store, None
    except Exception as e:
        logging.error(f'❌ Error creating RAG system from files: {str(e)}', exc_info=True)
        return None, None
    
def create_rag_from_single_file(file_path, path_to_faiss_index, is_new=False):
    """Create or update a RAG from a given single file."""
    try:
        if not os.path.isfile(file_path):
            logging.error(f"Invalid file path: {file_path}")
            return False

        # Handle where to copy the file
        destination_path = os.path.join(path_to_faiss_index, os.path.basename(file_path))
        shutil.copy(file_path, destination_path)
        
        # Example: Extract content (only for PDF or TXT)
        content = ''
        if file_path.endswith(".pdf"):
            content = "Extracted PDF content"
        elif file_path.endswith(".txt"):
            with open(destination_path, 'r', encoding='utf-8') as file:
                content = file.read()

        if not content.strip():
            logging.error("No text extracted from the file. Please check the file content.")
            return False

        logging.info(f"✅ New RAG created from file: {file_path}")
        return True
    except Exception as e:
        logging.error(f"❌ Error while creating RAG from file: {str(e)}", exc_info=True)
        return False