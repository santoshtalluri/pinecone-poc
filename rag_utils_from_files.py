import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings

def create_rag_system_from_files(folder_path, faiss_index_path):
    """
    Create a RAG system from files located in the specified folder.
    
    The files are used to create embeddings and build a FAISS index 
    that can be used for retrieval-augmented generation (RAG).

    Args:
        folder_path (str): Path to the folder containing files (PDF, TXT) to create RAG.
        faiss_index_path (str): Path to store the FAISS index.

    Returns:
        FAISS: The created FAISS vector store instance.
    """
    try:
        documents = []  # Extracted content from files
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_name.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
        
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(faiss_index_path)
        return vector_store, None
    except Exception as e:
        logging.error(f"❌ Failed to create RAG system: {str(e)}", exc_info=True)
        return None, None