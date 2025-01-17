import os
import logging
import re
from glob import glob
from flask import Blueprint, request, jsonify
from services.pinecone_service import get_pinecone_index
from utilities.pdf_extraction_utility import extract_text_from_pdf
from services.embedding_service import EmbeddingService,split_embedding_into_chunks
from services.pinecone_service import get_pinecone_index
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
import json
from config import Config
import numpy as np

# Load environment variables
load_dotenv()

create_new_rag_blueprint = Blueprint('create_new_rag', __name__)

# Pinecone metadata size limit
PINECONE_METADATA_LIMIT = 40960  # Bytes

# Maximum chunk size for splitting text
MAX_CHUNK_SIZE = 1000  # Words


def clean_text(text):
    """
    Clean unwanted headers, footers, and page numbers from the extracted text.
    
    Args:
        text (str): The raw extracted text to be cleaned.
    
    Returns:
        str: Cleaned text.
    """
    text = re.sub(r'P\s*a\s*g\s*e\s*\d+\s*\|\s*\d+', '', text)  # Remove page numbers
    text = re.sub(r'\n+', '\n', text)  # Remove extra newlines
    text = re.sub(r'\s+', ' ', text)  # Remove excessive whitespace
    return text.strip()


def split_text_into_chunks(text, max_size):
    """
    Splits the text into smaller chunks ensuring that each chunk is below the specified max size.
    
    Args:
        text (str): Text to be split.
        max_size (int): Maximum size of each chunk in bytes.
    
    Returns:
        list: List of text chunks.
    """
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


def split_metadata_into_vectors(metadata, vector_limit=40960):
    """
    Splits metadata into smaller chunks to fit within the Pinecone vector size limit.
    
    Args:
        metadata (dict): The original metadata to be split.
        vector_limit (int): The byte size limit for each vector.
    
    Returns:
        list: A list of smaller metadata chunks.
    """
    serialized_metadata = json.dumps(metadata)
    byte_size = len(serialized_metadata.encode('utf-8'))

    if byte_size <= vector_limit:
        return [metadata]  # If metadata fits, return as-is

    chunks = []
    current_chunk = {}

    for key, value in metadata.items():
        temp_chunk = current_chunk.copy()
        temp_chunk[key] = value
        temp_size = len(json.dumps(temp_chunk).encode('utf-8'))

        if temp_size > vector_limit:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = {key: value}
        else:
            current_chunk[key] = value

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


@create_new_rag_blueprint.route('', methods=['POST'])

def create_new_rag():
    """
    Endpoint to create a new RAG (Retrieval-Augmented Generation) by processing files in a specified folder.
    Extracts text from files, generates embeddings, and upserts them to a Pinecone index.

    Returns:
        Response (JSON): Success or error message.
    """
    try:
        data = request.get_json()
        folder_path = data.get('folder_path')
        rag_name = data.get('rag_name')

        if not folder_path or not os.path.isdir(folder_path):
            logging.error(f"❌ Invalid folder path provided: {folder_path}")
            return jsonify({"error": "Invalid folder path provided."}), 400
        
        if not rag_name:
            logging.error("❌ RAG name not provided.")
            return jsonify({"error": "RAG name is required."}), 400
        
        # Connect to Pinecone
        logging.info(f"🔄 Connecting to Pinecone to check RAG existence for namespace: {rag_name}")
        index = get_pinecone_index()
        if not index:
            logging.error("❌ Failed to connect to Pinecone index.")
            return jsonify({"error": "Failed to connect to Pinecone index."}), 500

        # Check if namespace already exists
        existing_indexes = index.describe_index_stats(namespace=rag_name)
        if existing_indexes and existing_indexes.get('namespaces', {}).get(rag_name, {}).get('vector_count', 0) > 0:
            logging.warning(f"⚠️ RAG name '{rag_name}' already exists.")
            return jsonify({
                "error": f"RAG name '{rag_name}' already exists. Use the 'add-file' endpoint to update files in this RAG."
            }), 400

        logging.info(f"📂 Processing files in folder: {folder_path} for RAG: {rag_name}")

        # Get all PDF and TXT files in the folder
        file_paths = glob(os.path.join(folder_path, "*"))
        file_paths = [f for f in file_paths if f.endswith('.pdf') or f.endswith('.txt')]

        if not file_paths:
            logging.warning(f"⚠️ No valid PDF or TXT files found in the folder: {folder_path}")
            return jsonify({"error": "No valid PDF or TXT files found in the folder."}), 400

        vectors = []
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

            # Split text into chunks
            chunks = split_text_into_chunks(full_text, MAX_CHUNK_SIZE)

            # Generate embeddings for each chunk
            
            for i, chunk in enumerate(chunks):
                embedding_service = EmbeddingService()
                embedding = embedding_service.generate_embeddings(chunk)
                #embedding = embedding_service.generate_embedding(chunk)
                if embedding is None:
                    logging.error(f"❌ Failed to generate embedding for chunk {i} of file: {file_path}")
                    continue

                # Ensure the embedding is a flat list of floats
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                elif isinstance(embedding, list):
                    embedding = [float(item) for sublist in embedding for item in (sublist if isinstance(sublist, list) else [sublist])]

                # Split embedding into smaller chunks if needed
                embedding_chunks = split_embedding_into_chunks(embedding, Config.PINECONE_INDEX_DIMENSION)

                for chunk_index, chunk_embedding in enumerate(embedding_chunks):
                    vectors.append({
                        "id": f"{os.path.basename(file_path)}-chunk-{i}-{chunk_index}",
                        "values": chunk_embedding,
                        "metadata": {
                            "file_name": os.path.basename(file_path),
                            "chunk_index": i,
                            "embedding_chunk_index": chunk_index,
                            "content": chunk
                        }
                    })

        if not vectors:
            logging.warning(f"⚠️ No vectors generated from files in {folder_path}")
            return jsonify({"error": "No vectors generated from the files in the folder."}), 400

        # Upsert vectors to Pinecone
        logging.info(f"📤 Preparing {len(vectors)} vectors for upsert to Pinecone")
        index = get_pinecone_index()
        if not index:
            logging.error("❌ Pinecone index connection failed.")
            return jsonify({"error": "Pinecone index connection failed."}), 500

        try:
            upsert_vectors = []
            for vector in vectors:
                metadata = vector.get("metadata", {})
                serialized_metadata = json.dumps(metadata)
                metadata_size = len(serialized_metadata.encode("utf-8"))

                # Check if metadata size exceeds the limit
                if metadata_size > PINECONE_METADATA_LIMIT:
                    logging.warning(f"⚠️ Metadata size for vector {vector['id']} exceeds limit ({metadata_size} bytes). Splitting...")
                    metadata_chunks = split_metadata_into_vectors(metadata, vector_limit=PINECONE_METADATA_LIMIT)
                    for i, chunk in enumerate(metadata_chunks):
                        upsert_vectors.append({
                            "id": f"{vector['id']}_{i}",
                            "values": vector["values"],
                            "metadata": chunk
                        })
                else:
                    upsert_vectors.append(vector)

            # Perform the upsert operation
            logging.info(f"📤 Upserting {len(upsert_vectors)} vectors to Pinecone")
            index.upsert(vectors=upsert_vectors, namespace=rag_name)

        except Exception as e:
            logging.error(f"❌ Failed to upsert vectors to Pinecone: {str(e)}", exc_info=True)
            return jsonify({"error": "Failed to upload vectors to Pinecone."}), 500

        return jsonify({
            "message": f"RAG '{rag_name}' created successfully.",
            "total_files": len(file_paths),
            "total_vectors": len(upsert_vectors)
        }), 200

    except Exception as e:
        logging.error(f"❌ Error in create_new_rag: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500
    
def create_vectors_from_text(text, rag_name):
    embedding_service = EmbeddingService()
    embedding = embedding_service.generate_embedding(text)

    # Ensure dimensions match the configured index
    if len(embedding) != Config.OPENAI_EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Embedding dimension mismatch: Expected {Config.OPENAI_EMBEDDING_DIMENSIONS}, got {len(embedding)}"
        )

    # Return vector with metadata
    return {
        "id": f"{rag_name}_vector",
        "values": embedding,
        "metadata": {
            "content": text,
            "rag_name": rag_name
        }
    }