import os
import logging
from flask import Blueprint, request, jsonify

add_file_blueprint = Blueprint('add_file', __name__)

@add_file_blueprint.route('', methods=['POST'])
def add_file():
    """
    Add a new file to the RAG system.

    This route takes a file as input and stores it in the appropriate 
    directory associated with the RAG.

    Returns:
        JSON: Success or failure message.
    """
    try:
        file = request.files['file']
        if file:
            file.save(os.path.join(Config.DATA_FOLDER, file.filename))
            return jsonify({"message": f"File {file.filename} uploaded successfully."}), 200
        else:
            return jsonify({"error": "No file provided"}), 400
    except Exception as e:
        logging.error(f"❌ Error uploading file: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500