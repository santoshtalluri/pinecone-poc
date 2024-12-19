import logging
import torch
from transformers import AutoTokenizer, AutoModel

# Local path to the model (update this path if needed)
LOCAL_MODEL_PATH = '/Users/santoshtalluri/Documents/MyDevProjects/models/hkunlp/instructor-xl/'

# Initialize global variables for models (avoid reloading every time)
instructor_tokenizer = None
instructor_model = None

def initialize_instructor_model():
    """Load Instructor-XL model from local path."""
    global instructor_tokenizer, instructor_model
    
    if instructor_tokenizer is None or instructor_model is None:
        logging.info(f"🧠 Loading Instructor-XL model from {LOCAL_MODEL_PATH}")
        
        # Load model from local path
        try:
            instructor_tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
            instructor_model = AutoModel.from_pretrained(LOCAL_MODEL_PATH)
            logging.info(f"✅ Instructor-XL model loaded successfully from {LOCAL_MODEL_PATH}")
        except Exception as e:
            logging.error(f"❌ Failed to load Instructor-XL model from {LOCAL_MODEL_PATH}: {str(e)}", exc_info=True)
            raise

def get_embedding(text):
    """Dynamically get embeddings based on the selected model."""
    try:
        logging.info(f"🔍 Generating embeddings using the 'instructor-xl' model")
        
        # Ensure model is initialized before generating embeddings
        initialize_instructor_model()
        
        return get_instructor_embeddings(text)
    except Exception as e:
        logging.error(f"❌ Error generating embeddings: {str(e)}", exc_info=True)
        raise

def get_instructor_embeddings(text):
    """Generate embeddings using the Instructor-XL model."""
    try:
        logging.info(f"🧠 Generating Instructor-XL embeddings for the provided text (first 100 chars): {text[:100]}...")
        
        # Tokenize input text
        inputs = instructor_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Pass input_ids as decoder_input_ids to prevent errors
        outputs = instructor_model(input_ids=inputs['input_ids'], decoder_input_ids=inputs['input_ids'])
        
        # Get the embedding from the model's output
        embedding = torch.mean(outputs.last_hidden_state, dim=1).squeeze().detach().numpy()
        
        logging.info(f"✅ Instructor-XL Embedding generated successfully with length: {len(embedding)}")
        return embedding
    except Exception as e:
        logging.error(f"❌ Instructor-XL embeddings failed: {str(e)}", exc_info=True)
        raise