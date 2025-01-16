import os
import logging
from flask import Blueprint, request, jsonify
from langchain_community.embeddings import OpenAIEmbeddings
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Blueprint
add_file_blueprint = Blueprint('add_file', __name__)

# Define constants
PINECONE_METADATA_LIMIT = 40960  # Pinecone metadata size limit in bytes


def split_text_into_chunks(text, max_size):
    """
    Split text into smaller chunks based on a specified maximum size.
    Each chunk ensures it does not exceed the Pinecone metadata size limit.
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


@add_file_blueprint.route('', methods=['POST'])
def add_file():
    """Add file content to Pinecone, handling large documents by splitting into chunks."""
    try:
        file = request.files['file']
        filename = file.filename
        file_path = os.path.join("./data", filename)
        file.save(file_path)

        # Extract text from the file
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Split text into chunks
        logging.info(f"📄 Splitting file '{filename}' into chunks for Pinecone.")
        chunks = split_text_into_chunks(text, PINECONE_METADATA_LIMIT)

        # Generate embeddings and upload each chunk to Pinecone
        embeddings = OpenAIEmbeddings()
        vectors = []
        for i, chunk in enumerate(chunks):
            vector_data = embeddings.embed_documents([chunk])
            vectors.append({
                "id": f"{filename}-chunk-{i}",  # Unique ID for each chunk
                "values": vector_data[0],
                "metadata": {
                    "content": chunk,
                    "file_name": filename,
                    "chunk_index": i
                }
            })

        # Upsert vectors to Pinecone
        logging.info(f"📤 Upserting {len(vectors)} vectors for file '{filename}' to Pinecone.")
        index.upsert(vectors=vectors)
        logging.info(f"✅ File '{filename}' added successfully to Pinecone.")

        return jsonify({"message": f"File '{filename}' added successfully, split into {len(chunks)} chunks."}), 200

    except Exception as e:
        logging.error(f"❌ Error adding file: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500