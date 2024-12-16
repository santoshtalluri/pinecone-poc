import logging
import os
import uuid  # ✅ Import uuid to generate unique identifiers
from flask import Blueprint, request, jsonify
from utilities.pdf_extraction_utility import extract_text_from_url
from rag_utils_from_files import create_rag_system_from_files
from config import Config  # ✅ Import Config

create_new_rag_blueprint = Blueprint('create_new_rag', __name__)

@create_new_rag_blueprint.route('', methods=['POST'])
def create_new_rag():
    try:
        data = request.get_json()
        url = data.get('url')
        file_path = data.get('file_path')
        rag_name = data.get('rag_name')  # New attribute to accept rag_name

        if not url and not file_path:
            return jsonify({"error": "Either 'url' or 'file_path' is required"}), 400

        if url:
            file_path, error = extract_text_from_url(url)
            if error:
                logging.error(f"❌ Failed to extract URL content. Error: {error}")
                return jsonify({"error": error}), 400

        folder_path = os.path.dirname(file_path)  # Get parent directory
        rag_id = rag_name if rag_name else f"rag_{uuid.uuid4().hex}"  # Use rag_name if provided, otherwise generate one
        unique_rag_folder = os.path.join(Config.FAISS_NEW_RAGS_PATH, rag_id)
        os.makedirs(unique_rag_folder, exist_ok=True)  # ✅ Ensure FAISS path exists

        logging.info(f"📁 Using folder path for RAG creation: {folder_path}")
        logging.info(f"🧠 RAG index will be stored at: {unique_rag_folder}")

        vector_store, _ = create_rag_system_from_files(folder_path, unique_rag_folder)
        if vector_store is None:
            logging.error(f"❌ Failed to create RAG system from folder: {folder_path}")
            return jsonify({"error": "Failed to create RAG system"}), 500

        return jsonify({"message": "RAG system created successfully", "faiss_index_path": unique_rag_folder}), 201
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500