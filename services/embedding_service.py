"""
embedding_service.py
====================

This module provides a unified interface to generate embeddings using selected models.
Supported models: openai, instructor-xl, ollama.

Usage:
- Configure the `EMBEDDING_MODEL` in `Config.py` to select the embedding model.
"""

import logging
import os
import torch
from transformers import AutoTokenizer, AutoModel
from langchain_openai.embeddings import OpenAIEmbeddings  # Updated import
from langchain.embeddings.openai import OpenAIEmbeddings
import requests
from config import Config

# Load embedding model configuration from Config
EMBEDDING_MODEL = Config.EMBEDDING_MODEL

# Global variables for Instructor-XL
instructor_tokenizer = None
instructor_model = None

class EmbeddingService:
    """
    A class to manage embeddings for selected models dynamically based on configuration.
    """

    def __init__(self):
        if Config.EMBEDDING_MODEL == "openai":
            self.embedding_model = OpenAIEmbeddings(
                model=Config.OPENAI_EMBEDDING_MODEL,
                openai_api_key=Config.OPENAI_API_KEY
            )
        else:
            raise ValueError(f"Unsupported embedding model: {Config.EMBEDDING_MODEL}")

        def generate_embedding(self, text):
            return self.embedding_model.embed_text(text)
        
        self.embedding_model = Config.EMBEDDING_MODEL
        print ("$$$$$$$$$$$$$$$$$$$$")
        print(Config.OPENAI_EMBEDDING_MODEL)
        print ("$$$$$$$$$$$$$$$$$$$$")
        self.tokenizer = None
        self.model = None
        self.load_model()

    def load_model(self):
        """
        Dynamically loads the embedding model based on the EMBEDDING_MODEL configuration.
        """
        logging.info(f"🔄 Loading embedding model: {EMBEDDING_MODEL}")

        try:
            if EMBEDDING_MODEL == "openai":
                # OpenAI Embeddings
                openai_api_key = Config.OPENAI_API_KEY
                if not openai_api_key:
                    raise ValueError("OpenAI API key is not set. Please configure it in .env or Config.")
                #self.embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
                self.embedding_model = OpenAIEmbeddings(
                model=Config.OPENAI_EMBEDDING_MODEL,
                openai_api_key=Config.OPENAI_API_KEY
                )
                logging.info("✅ OpenAI Embeddings loaded successfully.")

            elif EMBEDDING_MODEL == "instructor-xl":
                # Instructor-XL Embeddings
                global instructor_tokenizer, instructor_model
                if instructor_tokenizer is None or instructor_model is None:
                    instructor_tokenizer = AutoTokenizer.from_pretrained(Config.INSTRUCTOR_MODEL_PATH)
                    instructor_model = AutoModel.from_pretrained(Config.INSTRUCTOR_MODEL_PATH)
                    logging.info("✅ Instructor-XL model loaded successfully.")

            elif EMBEDDING_MODEL == "ollama":
                # Ollama On-Device Embeddings
                self.embedding_model = Config.OLLAMA_HOST
                logging.info(f"✅ Ollama on-device embedding service configured at {Config.OLLAMA_HOST}")

            else:
                raise ValueError(f"Unsupported embedding model: {EMBEDDING_MODEL}")

        except AttributeError as e:
            logging.error(f"❌ Missing attribute in Config: {str(e)}", exc_info=True)
            raise ValueError(f"Ensure Config has all required attributes: {str(e)}")

        except Exception as e:
            logging.error(f"❌ Failed to load the embedding model: {str(e)}", exc_info=True)
            raise

    def generate_embeddings(self, text):
        """
        Generates embeddings for the given text using the loaded model.

        Args:
            text (str): The input text to generate embeddings for.

        Returns:
            list: A list of embedding vectors.
        """
        try:
            if EMBEDDING_MODEL == "openai":
                return self.embedding_model.embed_documents([text])

            elif EMBEDDING_MODEL == "instructor-xl":
                return self.get_instructor_embeddings(text)

            elif EMBEDDING_MODEL == "ollama":
                return self._generate_ollama_embeddings(text)

            else:
                raise ValueError(f"Unsupported embedding model for generation: {EMBEDDING_MODEL}")

        except Exception as e:
            logging.error(f"❌ Error generating embeddings: {str(e)}", exc_info=True)
            raise

    def get_instructor_embeddings(self, text):
        """
        Generate embeddings using the Instructor-XL model.

        Args:
            text (str): The input text.

        Returns:
            list: Embedding vector from Instructor-XL.
        """
        try:
            inputs = instructor_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            outputs = instructor_model(input_ids=inputs['input_ids'], decoder_input_ids=inputs['input_ids'])
            embedding = torch.mean(outputs.last_hidden_state, dim=1).squeeze().detach().numpy()
            logging.info(f"✅ Instructor-XL Embedding generated successfully with length: {len(embedding)}")
            return embedding.tolist()
        except Exception as e:
            logging.error(f"❌ Instructor-XL embeddings failed: {str(e)}", exc_info=True)
            raise

    def _generate_ollama_embeddings(self, text):
        """
        Generates embeddings using the Ollama API.

        Args:
            text (str): The input text.

        Returns:
            list: Embedding vector from Ollama.
        """
        try:
            url = f"{self.embedding_model}/api/embeddings"  # Updated endpoint
            payload = {
                "prompt": text,
                "model": "mxbai-embed-large"  # Use a valid embedding model
            }
            headers = {"Content-Type": "application/json"}

            response = requests.post(url, json=payload)
            response.raise_for_status()

            embedding = response.json().get("embedding")
            if not embedding:
                logging.error(f"❌ Ollama API response missing 'embedding': {response.json()}")
                raise ValueError("Failed to retrieve embedding from Ollama response.")

            logging.info("✅ Ollama embedding generated successfully.")
            return embedding

        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Ollama API request failed: {str(e)}", exc_info=True)
            raise ValueError("Ollama API request failed.")

        except Exception as e:
            logging.error(f"❌ Unexpected error in Ollama embeddings: {str(e)}", exc_info=True)
            raise


# Standalone function for easy access
embedding_service_instance = EmbeddingService()

def get_embedding(text):
    """
    Generate embeddings for the given text using the configured model.

    Args:
        text (str): The input text.

    Returns:
        list: A list of embedding vectors.
    """
    return embedding_service_instance.generate_embeddings(text)

def split_embedding_into_chunks(embedding, max_dim):
    """
    Splits a large embedding into smaller chunks with dimensions up to max_dim.

    Args:
        embedding (list): The original embedding vector.
        max_dim (int): The maximum dimension for each chunk.

    Returns:
        list: A list of smaller embeddings.
    """
    return [embedding[i:i + max_dim] for i in range(0, len(embedding), max_dim)]

def adjust_embedding_dimensions(embedding, target_dim):
    """
    Adjusts the dimensions of the embedding to match the target dimension.
    Handles nested structures and unexpected formats.

    Args:
        embedding (list): The original embedding vector.
        target_dim (int): The target dimension for the embedding.

    Returns:
        list: Adjusted embedding vector.
    """
    # Ensure embedding is a flat list
    if isinstance(embedding[0], list):
        embedding = embedding[0]  # Handle nested structure
    if len(embedding) > target_dim:
        return embedding[:target_dim]  # Truncate
    elif len(embedding) < target_dim:
        return embedding + [0.0] * (target_dim - len(embedding))  # Pad
    return embedding