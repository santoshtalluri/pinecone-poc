import os
import logging

DEFAULT_RAG_FILE_PATH = '/Users/santoshtalluri/Documents/MyDevProjects/MyProject/default_rag.txt'

def get_default_rag():
    """Reads the default RAG name from default_rag.txt"""
    try:
        if os.path.exists(DEFAULT_RAG_FILE_PATH):
            with open(DEFAULT_RAG_FILE_PATH, 'r') as file:
                rag_name = file.read().strip()
                logging.info(f"🧠 Default RAG loaded from file: {rag_name}")
                return rag_name
        else:
            logging.warning(f"⚠️ No default RAG file found at {DEFAULT_RAG_FILE_PATH}.")
            return None
    except Exception as e:
        logging.error(f"❌ Failed to read default RAG from file: {str(e)}", exc_info=True)
        return None