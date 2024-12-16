import os
import logging
from flask import Blueprint, jsonify

# Blueprint for getting the default RAG
get_default_rag_blueprint = Blueprint('get_default_rag', __name__)

DEFAULT_RAG_FILE_PATH = '/Users/santoshtalluri/Documents/MyDevProjects/MyProject/default_rag.txt'

@get_default_rag_blueprint.route('', methods=['GET'])
def get_default_rag():
    """
    Get the current default RAG.

    This route reads the name of the current default RAG from 
    default_rag.txt and returns it.

    Returns:
        JSON: The name of the default RAG or a message if no RAG is set.
    """
    try:
        if os.path.exists(DEFAULT_RAG_FILE_PATH):
            with open(DEFAULT_RAG_FILE_PATH, 'r') as file:
                rag_name = file.read().strip()
                if rag_name:
                    logging.info(f"🧠 Default RAG loaded from file: {rag_name}")
                    return jsonify({"default_rag": rag_name}), 200
                else:
                    logging.warning(f"⚠️ Default RAG file is empty.")
                    return jsonify({"message": "No default RAG has been set."}), 200
        else:
            logging.warning(f"⚠️ Default RAG file not found at {DEFAULT_RAG_FILE_PATH}.")
            return jsonify({"message": "No default RAG has been set."}), 200
    except Exception as e:
        logging.error(f"❌ Error retrieving default RAG: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500