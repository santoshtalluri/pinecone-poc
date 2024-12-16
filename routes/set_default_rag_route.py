import os
import logging
from flask import Blueprint, request, jsonify

# Blueprint for setting the default RAG
set_default_rag_blueprint = Blueprint('set_default_rag', __name__)

DEFAULT_RAG_FILE_PATH = '/Users/santoshtalluri/Documents/MyDevProjects/MyProject/default_rag.txt'

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

        # ✅ Write the default RAG name to the file
        with open(DEFAULT_RAG_FILE_PATH, 'w') as file:
            file.write(rag_name)
        logging.info(f"✅ Successfully set '{rag_name}' as the default RAG.")

        return jsonify({"message": f"RAG '{rag_name}' is now the default RAG."}), 200
    except Exception as e:
        logging.error(f"❌ Error setting default RAG: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500