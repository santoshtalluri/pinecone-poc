import logging
from pinecone import Pinecone, ServerlessSpec
from config import Config


def get_pinecone_index(index_name=None):
    """
    Connects to Pinecone and returns the index.

    Args:
        index_name (str, optional): The name of the Pinecone index to connect to.
                                    Defaults to the value of PINECONE_INDEX_NAME from Config.

    Returns:
        Pinecone Index object if successful, None otherwise.
    """
    try:
        # Step 1: Create a Pinecone client instance
        logging.info("🔄 Initializing Pinecone client...")
        pinecone_client = Pinecone(api_key=Config.PINECONE_API_KEY)

        # Step 2: Determine the index name
        index_name = index_name or Config.PINECONE_INDEX_NAME
        logging.info(f"📘 Using Pinecone index name: {index_name}")

        # Step 3: List existing indexes
        existing_indexes = pinecone_client.list_indexes().names()
        logging.info(f"📋 Existing Pinecone indexes: {existing_indexes}")

        # Step 4: Check if the index exists; if not, create it
        if index_name not in existing_indexes:
            logging.info(f"🔄 Creating Pinecone index: {index_name}")
            pinecone_client.create_index(
                name=index_name,
                dimension=Config.OPENAI_EMBEDDING_DIMENSIONS,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",  # Replace with your cloud provider if needed
                    region="us-west-2"  # Replace with your region if needed
                )
            )
            logging.info(f"✅ Pinecone index '{index_name}' created successfully.")

        # Step 5: Connect to the Pinecone index
        logging.info(f"🔄 Connecting to Pinecone index: {index_name}")
        #index = pinecone_client.index(index_name)
        index = pinecone_client.Index(index_name)
        logging.info(f"✅ Successfully connected to Pinecone index: '{index_name}'")
        return index

    except Exception as e:
        logging.error(f"❌ Error initializing Pinecone: {str(e)}", exc_info=True)
        return None