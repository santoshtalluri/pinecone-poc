import os
import logging
from flask import Blueprint, request, jsonify
from pinecone import Pinecone
from config import Config

delete_rag_blueprint = Blueprint('delete_rag', __name__)

DEFAULT_RAG_FILE_PATH = '/Users/santoshtalluri/Documents/MyDevProjects/pinecone-poc/default_rag.txt'

def get_default_rag():
    """
    Retrieve the current default RAG from the default_rag.txt file.
    """
    try:
        if os.path.exists(DEFAULT_RAG_FILE_PATH):
            with open(DEFAULT_RAG_FILE_PATH, "r") as file:
                return file.read().strip()
        return None
    except Exception as e:
        logging.error(f"❌ Error reading default RAG: {str(e)}")
        return None

@delete_rag_blueprint.route('', methods=['DELETE'])
def delete_rag():
    """
    Delete a specific RAG (index) from Pinecone.

    Args:
        rag_name (str): The name of the RAG to delete.

    Returns:
        JSON: Success or failure message.
    """
    try:
        data = request.get_json()
        rag_name = data.get('rag_name')

        if not rag_name:
            logging.error("❌ 'rag_name' is required but was not provided.")
            return jsonify({"error": "'rag_name' is required"}), 400

        # Retrieve the default RAG
        default_rag = get_default_rag()
        if default_rag == rag_name:
            logging.error(f"❌ Cannot delete default RAG '{rag_name}'.")
            return jsonify({"error": f"Default RAG '{rag_name}' cannot be deleted. Please change the default RAG first."}), 400

        # Initialize Pinecone client
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)

        # Check if the index exists
        existing_indexes = pc.list_indexes().names()
        if rag_name not in existing_indexes:
            logging.error(f"❌ RAG '{rag_name}' does not exist.")
            return jsonify({"error": f"RAG '{rag_name}' does not exist. Verify the name."}), 404

        # Delete the index
        logging.info(f"🔄 Deleting RAG (index): {rag_name}")
        pc.delete_index(rag_name)
        logging.info(f"✅ Successfully deleted RAG (index): {rag_name}")

        return jsonify({"message": f"RAG '{rag_name}' deleted successfully."}), 200

    except Exception as e:
        logging.error(f"❌ Error deleting RAG: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500