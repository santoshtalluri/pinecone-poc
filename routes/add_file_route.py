import os
from flask import Blueprint, request, jsonify
from rag_utils_from_files import create_rag_from_single_file
from config import Config

add_file_blueprint = Blueprint('add_file', __name__)

@add_file_blueprint.route('', methods=['POST'])
def add_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file:
        file_path = os.path.join(Config.DATA_FOLDER, file.filename)
        file.save(file_path)
        success = create_rag_from_single_file(file_path, Config.FAISS_INDEX_PATH)
        
        if success:
            return jsonify({"message": f"File '{file.filename}' added successfully"}), 200
        else:
            return jsonify({"error": "Failed to add file"}), 500