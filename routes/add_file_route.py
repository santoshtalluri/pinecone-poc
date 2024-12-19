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

@add_file_blueprint.route('', methods=['POST'])
def add_file():
    """Add file content to Pinecone."""
    try:
        file = request.files['file']
        filename = file.filename
        file_path = os.path.join("./data", filename)
        file.save(file_path)

        # Extract text
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Generate embeddings
        embeddings = OpenAIEmbeddings()
        vector_data = embeddings.embed_documents([text])

        # Upload to Pinecone
        response = index.upsert(vectors=[{"id": filename, "values": vector_data[0]}])
        logging.info(f"✅ File {filename} added to Pinecone.")
        return jsonify({"message": f"File '{filename}' added successfully."}), 200
    except Exception as e:
        logging.error(f"❌ Error adding file: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500