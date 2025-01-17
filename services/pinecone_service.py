import logging
from pinecone import Pinecone, ServerlessSpec
from config import Config

# Initialize Pinecone client
pinecone_client = Pinecone(
    api_key=Config.PINECONE_API_KEY
)

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
        logging.info("🔄 Initializing Pinecone client...")
        
        index_name = index_name or Config.PINECONE_INDEX_NAME
        logging.info(f"📘 Using Pinecone index name: {index_name}")

        existing_indexes = pinecone_client.list_indexes().names()
        logging.info(f"📋 Existing Pinecone indexes: {existing_indexes}")

        if index_name not in existing_indexes:
            raise ValueError(f"Index '{index_name}' does not exist in Pinecone.")

        logging.info(f"🔄 Connecting to Pinecone index: {index_name}")
        index = pinecone_client.Index(index_name)
        logging.info(f"✅ Successfully connected to Pinecone index: '{index_name}'")
        return index

    except Exception as e:
        logging.error(f"❌ Error initializing Pinecone: {str(e)}", exc_info=True)
        return None


def create_pinecone_index(index_name, dimensions, embedding_model=None):
    """
    Creates a Pinecone index with the specified name and dimensions.

    Args:
        index_name (str): The name of the index to create.
        dimensions (int): The dimensionality of the vectors in the index.
        embedding_model (str): The embedding model to use.
    """
    try:
        # Check if the index already exists
        existing_indexes = pinecone_client.list_indexes().names()
        if index_name in existing_indexes:
            logging.info(f"Index '{index_name}' already exists. Skipping creation.")
            return

        # Select embedding model
        if embedding_model is None:
            embedding_model = (
                "text-embedding-3-large" if Config.EMBEDDING_MODEL == "openai" else "multilingual-e5-large"
            )

        # Log the selected embedding model
        logging.info(
            f"🔄 Creating Pinecone index '{index_name}' with dimensions {dimensions} and model '{embedding_model}'"
        )

        # Create the Pinecone index
        pinecone_client.create_index(
            name=index_name,
            dimension=dimensions,
            metric="cosine",  # Adjust the metric as needed
            spec=ServerlessSpec(
                cloud="aws",   # This remains "aws"
                region="us-east-1"  # Ensure the region is "us-east-1"
            )
        )
        logging.info(f"✅ Successfully created Pinecone index: {index_name}")
        
        # Dynamically update the default index name to the newly created RAG
        Config.PINECONE_INDEX_NAME = index_name
        logging.info(f"✅ Default Pinecone index updated to: {Config.PINECONE_INDEX_NAME}")
    except Exception as e:
        logging.error(f"❌ Error creating Pinecone index '{index_name}': {str(e)}", exc_info=True)
        raise