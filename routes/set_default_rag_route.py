import os
import logging
from flask import Blueprint, request, jsonify
from pinecone import Pinecone
from config import Config

# Blueprint for setting the default RAG
set_default_rag_blueprint = Blueprint('set_default_rag', __name__)

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

def set_default_rag_in_file(rag_name):
    """
    Update the default RAG in the default_rag.txt file.
    """
    try:
        with open(DEFAULT_RAG_FILE_PATH, "w") as file:
            file.write(rag_name)
        logging.info(f"✅ Default RAG updated to: {rag_name}")
    except Exception as e:
        logging.error(f"❌ Error updating default RAG: {str(e)}")
        raise

def validate_rag_name(rag_name):
    """
    Validate if the provided RAG name exists in Pinecone indexes.
    """
    try:
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        existing_indexes = pc.list_indexes().names()
        return rag_name in existing_indexes
    except Exception as e:
        logging.error(f"❌ Error validating RAG name: {str(e)}")
        return False

@set_default_rag_blueprint.route('', methods=['POST'])
def set_default_rag():
    """
    Set a specific RAG as the default RAG.

    This route takes a POST request with the `rag_name` as input
    and sets the default RAG. The name of the RAG is saved in
    default_rag.txt.

    Returns:
        JSON: Success message or error message.
    """
    try:
        data = request.get_json()
        rag_name = data.get('rag_name')

        if not rag_name:
            logging.error("❌ 'rag_name' is required but was not provided.")
            return jsonify({"error": "'rag_name' is required"}), 400

        # Check if the file is empty or the first index is being set
        current_default_rag = get_default_rag()
        if not current_default_rag:
            logging.info(f"📌 No default RAG set. Setting '{rag_name}' as the default RAG.")
            if validate_rag_name(rag_name):
                set_default_rag_in_file(rag_name)
                return jsonify({"message": f"RAG '{rag_name}' is now the default RAG."}), 200
            else:
                return jsonify({"error": f"RAG '{rag_name}' does not exist. Verify the name."}), 400

        # Check if the provided RAG name is already the default
        if current_default_rag == rag_name:
            logging.info(f"📌 RAG '{rag_name}' is already set as the default RAG.")
            return jsonify({"message": f"RAG '{rag_name}' is already the default RAG."}), 200

        # Validate if the provided RAG name exists
        if not validate_rag_name(rag_name):
            logging.error(f"❌ RAG '{rag_name}' does not exist.")
            return jsonify({"error": f"RAG '{rag_name}' does not exist. Verify the name."}), 400

        # Update the default RAG
        set_default_rag_in_file(rag_name)
        return jsonify({"message": f"RAG '{rag_name}' is now the default RAG."}), 200

    except Exception as e:
        logging.error(f"❌ Error setting default RAG: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500