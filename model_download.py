import logging
import os
from transformers import AutoTokenizer, AutoModel

# Define the local path where the model will be stored
local_model_path = '/Users/santoshtalluri/Documents/MyDevProjects/models/hkunlp/instructor-xl/'

def download_and_save_model():
    """Download and save the Instructor-XL model and tokenizer."""
    try:
        logging.info(f"📥 Starting to download and save the Instructor-XL model to {local_model_path}...")

        # Check if the model is already downloaded
        if os.path.exists(os.path.join(local_model_path, 'pytorch_model.bin')):
            logging.info(f"✅ Model already exists at {local_model_path}. No need to re-download.")
            return

        # Download and save the tokenizer
        logging.info(f"📦 Downloading tokenizer for Instructor-XL...")
        tokenizer = AutoTokenizer.from_pretrained('hkunlp/instructor-xl', force_download=True)
        tokenizer.save_pretrained(local_model_path)
        logging.info(f"✅ Tokenizer saved successfully at {local_model_path}.")

        # Download and save the model
        logging.info(f"📦 Downloading model for Instructor-XL...")
        model = AutoModel.from_pretrained('hkunlp/instructor-xl', force_download=True)
        model.save_pretrained(local_model_path)
        logging.info(f"✅ Model saved successfully at {local_model_path}.")

        print(f"✅ Model and tokenizer saved at {local_model_path}")

    except Exception as e:
        logging.error(f"❌ Failed to download and save the Instructor-XL model: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    # Enable logging to track the progress of downloads
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("🚀 Starting model download process")
    download_and_save_model()
    logging.info("🎉 Model download process complete")