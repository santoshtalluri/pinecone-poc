import os
import logging
from pinecone import Pinecone, ServerlessSpec

def get_pinecone_index(index_name=None):
    """
    Connects to Pinecone and returns the index.
    
    Args:
        index_name (str, optional): The name of the Pinecone index to connect to. 
                                    Defaults to the value of PINECONE_INDEX_NAME from the environment.
    
    Returns:
        Pinecone Index object if successful, None otherwise.
    """
    try:
        # Step 1: Load API key from environment variables
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("❌ PINECONE_API_KEY is not set in .env")

        # Step 2: Initialize the Pinecone instance
        pc = Pinecone(api_key=api_key)
        logging.info("✅ Successfully initialized Pinecone with API key.")

        # Step 3: Check if index name is provided, otherwise use the default from .env
        index_name = index_name or os.getenv('PINECONE_INDEX_NAME', 'rag-index')
        logging.info(f"📘 Using Pinecone index name: {index_name}")
        
        # Step 4: Check if the index exists, if not, raise an error
        if index_name not in pc.list_indexes().names():
            logging.error(f"❌ Pinecone index '{index_name}' does not exist.")
            return None

        # Step 5: Connect to the Pinecone index
        index = pc.Index(index_name)
        logging.info(f"✅ Successfully connected to Pinecone index: '{index_name}'")
        return index
    
    except Exception as e:
        logging.error(f"❌ Error initializing Pinecone: {str(e)}", exc_info=True)
        return None