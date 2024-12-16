import os
import logging
from flask import Blueprint, request, jsonify
from config import Config
from utilities.default_rag_utility import get_default_rag

remove_file_blueprint = Blueprint('remove_file', __name__)

@remove_file_blueprint.route('', methods=['DELETE'])
def remove_file():
    rag_name = request.args.get('rag_name', get_default_rag())  # ✅ Use default RAG if no rag_name provided
    try:
        file_name = request.args.get('file_name')
        rag_name = request.args.get('rag_name', 'default')

        if not file_name:
            return jsonify({"error": "file_name is required"}), 400

        if rag_name == 'default':
            folder_path = Config.FAISS_INDEX_PATH
        else:
            folder_path = os.path.join(Config.FAISS_NEW_RAGS_PATH, rag_name)

        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path):
            return jsonify({"error": f"File '{file_name}' not found."}), 404

        os.remove(file_path)
        return jsonify({"message": f"File '{file_name}' removed successfully."}), 200
    except Exception as e:
        logging.error(f"❌ Error removing file: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500