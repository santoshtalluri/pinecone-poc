import os
import logging
import re
from glob import glob
from flask import Blueprint, request, jsonify
from services.pinecone_service import get_pinecone_index, create_pinecone_index
from utilities.pdf_extraction_utility import extract_text_from_pdf
from services.embedding_service import EmbeddingService
from config import Config
import json
from pinecone import Pinecone
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

create_new_rag_blueprint = Blueprint('create_new_rag', __name__)

# Pinecone metadata size limit
PINECONE_METADATA_LIMIT = 40960  # Bytes
DEFAULT_RAG_FILE = "/Users/santoshtalluri/Documents/MyDevProjects/pinecone-poc/default_rag.txt"

def set_default_rag(rag_name):
    """
    Update the default RAG in the default_rag.txt file.
    """
    try:
        with open(DEFAULT_RAG_FILE, "w") as f:
            f.write(rag_name)
        logging.info(f"✅ Default RAG updated to: {rag_name}")
    except Exception as e:
        logging.error(f"❌ Error updating default RAG: {str(e)}")
        raise

def get_default_rag():
    """
    Retrieve the current default RAG from the default_rag.txt file.
    """
    try:
        if os.path.exists(DEFAULT_RAG_FILE):
            with open(DEFAULT_RAG_FILE, "r") as f:
                return f.read().strip()
        return None
    except Exception as e:
        logging.error(f"❌ Error reading default RAG: {str(e)}")
        return None

def get_max_chunk_size():
    """Determine the maximum chunk size based on the embedding model."""
    if Config.EMBEDDING_MODEL == "openai" and Config.OPENAI_EMBEDDING_MODEL == "text-embedding-3-large":
        return 5000
    elif Config.EMBEDDING_MODEL == "ollama" and Config.OLLAMA_EMBEDDING_MODEL == "mxbai-embed-large":
        return 400
    else:
        return 1000  # Default fallback


def clean_text(text):
    text = re.sub(r'P\s*a\s*g\s*e\s*\d+\s*\|\s*\d+', '', text)  # Remove page numbers
    text = re.sub(r'\n+', '\n', text)  # Remove extra newlines
    text = re.sub(r'\s+', ' ', text)  # Remove excessive whitespace
    return text.strip()


def split_text_into_chunks(text, max_size):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk + [word])) <= max_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


@create_new_rag_blueprint.route('', methods=['POST'])
def create_new_rag():
    """
    Endpoint to create a new RAG (Retrieval-Augmented Generation) by processing files in a specified folder.
    Creates a new Pinecone index and stores each file as a separate namespace.
    """
    try:
        # Initialize Pinecone client
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        
        data = request.get_json()
        folder_path = data.get('folder_path')
        rag_name = data.get('rag_name')

        if not folder_path or not os.path.isdir(folder_path):
            logging.error(f"❌ Invalid folder path provided: {folder_path}")
            return jsonify({"error": "Invalid folder path provided."}), 400

        if not rag_name:
            logging.error("❌ RAG name not provided.")
            return jsonify({"error": "RAG name is required."}), 400

        # Check if the index already exists
        existing_indexes = pc.list_indexes().names()
        if rag_name in existing_indexes:
            logging.error(f"❌ An index with the name '{rag_name}' already exists.")
            return jsonify({
                "error": f"An index with the name '{rag_name}' already exists. "
                         "Use the 'add-file' or 'add-url' endpoints to add files to this index."
            }), 400

        # Determine embedding dimensions and model
        index_dimensions = Config.get_index_dimensions()
        embedding_model = (
            "text-embedding-3-large" if Config.EMBEDDING_MODEL == "openai" else "multilingual-e5-large"
        )

        # Create a new Pinecone index
        logging.info(f"🔄 Creating Pinecone index: {rag_name} with dimensions {index_dimensions}")
        create_pinecone_index(rag_name, index_dimensions, embedding_model=embedding_model)

        # If this is the first index, set it as the default RAG
        if not get_default_rag():
            logging.info(f"📌 No default RAG set. Setting '{rag_name}' as the default RAG.")
            set_default_rag(rag_name)

        # Get all PDF and TXT files in the folder
        file_paths = glob(os.path.join(folder_path, "*"))
        file_paths = [f for f in file_paths if f.endswith('.pdf') or f.endswith('.txt')]

        if not file_paths:
            logging.warning(f"⚠️ No valid PDF or TXT files found in the folder: {folder_path}")
            return jsonify({"error": "No valid PDF or TXT files found in the folder."}), 400

        # Get max chunk size dynamically
        max_chunk_size = get_max_chunk_size()

        total_vectors = 0

        for file_path in file_paths:
            logging.info(f"📄 Processing file: {file_path}")

            # Extract text
            if file_path.endswith('.pdf'):
                full_text = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    full_text = f.read()

            if not full_text.strip():
                logging.warning(f"⚠️ No content extracted from {file_path}. Skipping.")
                continue

            # Clean and split text into chunks
            clean_content = clean_text(full_text)
            chunks = split_text_into_chunks(clean_content, max_chunk_size)

            # Generate embeddings and prepare vectors
            vectors = []
            for i, chunk in enumerate(chunks):
                embedding_service = EmbeddingService()
                embedding = embedding_service.generate_embeddings(chunk)

                if embedding is None:
                    logging.error(f"❌ Failed to generate embedding for chunk {i} of file: {file_path}")
                    continue

                # Flatten the embedding if it is nested
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.flatten().tolist()
                elif isinstance(embedding, list) and isinstance(embedding[0], list):
                    embedding = [item for sublist in embedding for item in sublist]

                # Validate the embedding is a list of floats
                if not all(isinstance(val, (float, int)) for val in embedding):
                    logging.error(f"❌ Invalid embedding format for chunk {i} of file: {file_path}")
                    continue

                vectors.append({
                    "id": f"{os.path.basename(file_path)}-chunk-{i}",
                    "values": embedding,
                    "metadata": {
                        "file_name": os.path.basename(file_path),
                        "chunk_index": i,
                        "content": chunk
                    }
                })

            if not vectors:
                logging.warning(f"⚠️ No vectors generated for file: {file_path}. Skipping.")
                continue

            # Upsert vectors to a separate namespace for the file
            namespace = os.path.basename(file_path).replace(" ", "_").lower()
            logging.info(f"📤 Upserting {len(vectors)} vectors to Pinecone in namespace: {namespace}")

            index = get_pinecone_index(index_name=rag_name)
            index.upsert(vectors=vectors, namespace=namespace)
            total_vectors += len(vectors)

        return jsonify({
            "message": f"RAG '{rag_name}' created successfully.",
            "total_files": len(file_paths),
            "total_vectors": total_vectors
        }), 200

    except Exception as e:
        logging.error(f"❌ Error in create_new_rag: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500