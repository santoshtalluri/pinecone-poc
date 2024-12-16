import os
import logging
from flask import Blueprint, request, jsonify
from config import Config

list_files_blueprint = Blueprint('list_files', __name__)

@list_files_blueprint.route('', methods=['GET'])
def list_files():
    try:
        rag_name = request.args.get('rag_name', 'default')
        if rag_name == 'default':
            folder_path = Config.FAISS_INDEX_PATH
        else:
            folder_path = os.path.join(Config.FAISS_NEW_RAGS_PATH, rag_name)
        
        if not os.path.exists(folder_path):
            return jsonify({"error": f"RAG '{rag_name}' not found."}), 404

        files = os.listdir(folder_path)
        return jsonify({"files": files}), 200
    except Exception as e:
        logging.error(f"❌ Error listing files: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500