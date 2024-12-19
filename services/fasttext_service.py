import fasttext.util
import os
import logging
import numpy as np  # ✅ Import NumPy for embedding validation
from config import Config  # Import paths from config

# Use paths from Config
FASTTEXT_MODEL_DIR = Config.FASTTEXT_HOME
FASTTEXT_MODEL_PATH = Config.FASTTEXT_MODEL_PATH


def ensure_fasttext_model():
    """Ensure the FastText model is downloaded and available in the project directory."""
    try:
        # Step 1: Create the .fasttext directory if it doesn't exist
        if not os.path.exists(FASTTEXT_MODEL_DIR):
            logging.info(f"📁 Creating FastText directory at {FASTTEXT_MODEL_DIR}")
            os.makedirs(FASTTEXT_MODEL_DIR, exist_ok=True)

        # Step 2: Check if the model already exists
        if os.path.isfile(FASTTEXT_MODEL_PATH):
            logging.info(f"✅ FastText model already exists at {FASTTEXT_MODEL_PATH}")
            return

        # Step 3: Download the FastText model directly to the correct location
        logging.info(f"📥 Downloading FastText model directly to {FASTTEXT_MODEL_PATH}")
        download_url = 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.en.300.bin.gz'
        temp_gz_path = os.path.join(FASTTEXT_MODEL_DIR, 'cc.en.300.bin.gz')
        
        # Download the model
        if not os.path.isfile(temp_gz_path):
            logging.info(f"🌐 Downloading FastText model from {download_url} to {temp_gz_path}")
            os.system(f"curl -o {temp_gz_path} {download_url}")

        # Extract the gzipped file
        logging.info(f"📦 Extracting FastText model from {temp_gz_path}")
        os.system(f"gunzip -f {temp_gz_path}")
        
        # Rename extracted file to match expected model path
        extracted_path = os.path.join(FASTTEXT_MODEL_DIR, 'cc.en.300.bin')
        if os.path.isfile(extracted_path):
            logging.info(f"🚚 Moving FastText model from {extracted_path} to {FASTTEXT_MODEL_PATH}")
            os.rename(extracted_path, FASTTEXT_MODEL_PATH)
        
        if os.path.isfile(FASTTEXT_MODEL_PATH):
            logging.info(f"✅ FastText model is ready at {FASTTEXT_MODEL_PATH}")
        else:
            logging.error(f"❌ FastText model not found after download at {FASTTEXT_MODEL_PATH}")
    except Exception as e:
        logging.error(f"❌ Failed to ensure FastText model: {str(e)}", exc_info=True)


def load_fasttext_model():
    """Loads the FastText model from the project-level .fasttext directory."""
    try:
        ensure_fasttext_model()  # Ensure the model exists

        if not os.path.isfile(FASTTEXT_MODEL_PATH):
            logging.error(f"❌ FastText model not found at {FASTTEXT_MODEL_PATH}")
            return None

        logging.info(f"📥 Loading FastText model from {FASTTEXT_MODEL_PATH}")
        ft = fasttext.load_model(FASTTEXT_MODEL_PATH)
        logging.info(f"✅ Successfully loaded FastText model from {FASTTEXT_MODEL_PATH}")
        return ft
    except Exception as e:
        logging.error(f"❌ Failed to load FastText model: {str(e)}", exc_info=True)
        return None


def get_fasttext_embeddings(text):
    """Generate FastText embeddings for the input text."""
    try:
        ft = load_fasttext_model()
        if not ft:
            logging.error("❌ Failed to load FastText model.")
            return []

        if not text.strip():
            logging.warning("⚠️ The input text is empty. Returning an empty embedding.")
            return []

        embedding = ft.get_sentence_vector(text)

        if embedding is None:
            logging.error("❌ FastText embedding is None. Something went wrong.")
            return []

        if not isinstance(embedding, (list, np.ndarray)):
            logging.error(f"❌ Embedding is not a list or NumPy array. Type: {type(embedding)}")
            return []

        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()  # Convert NumPy array to list
        
        if len(embedding) == 0:
            logging.error("❌ FastText embedding is empty.")
            return []

        logging.info(f"✅ Successfully generated embedding for text: {text[:50]}... Embedding (first 10 values): {embedding[:10]}")
        return [embedding]  # Wrap in a list to maintain consistency for multiple embeddings
    except Exception as e:
        logging.error(f"❌ Error generating FastText embedding: {str(e)}", exc_info=True)
        return []