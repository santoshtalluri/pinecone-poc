import os
import logging
from flask import Blueprint, request, jsonify
from config import Config  # ✅ Import the Config class

remove_file_blueprint = Blueprint('remove_file', __name__)

@remove_file_blueprint.route('', methods=['DELETE'])
def remove_file():
    # 🔥 Ensure file_name is not None
    file_name = request.args.get('file_name')
    if not file_name:
        logging.error("❌ file_name is missing in request arguments.")
        return jsonify({"error": "file_name is required"}), 400

    # 🔥 Ensure Config.DATA_FOLDER is valid
    if not Config.DATA_FOLDER:
        logging.error("❌ Config.DATA_FOLDER is not set in config.py.")
        return jsonify({"error": "DATA_FOLDER is not properly configured"}), 500

    file_path = os.path.join(Config.DATA_FOLDER, file_name)
    logging.info(f"🗑️ Attempting to delete file: {file_path}")
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"✅ File '{file_name}' removed successfully.")
            return jsonify({"message": f"File '{file_name}' removed successfully"}), 200
        else:
            logging.warning(f"⚠️ File not found: {file_path}")
            return jsonify({"error": f"File '{file_name}' not found"}), 404
    except Exception as e:
        logging.error(f'❌ Error while removing file: {str(e)}', exc_info=True)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500