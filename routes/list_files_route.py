import os
from flask import Blueprint, jsonify
from config import Config  # ✅ Import the Config class

list_files_blueprint = Blueprint('list_files', __name__)

@list_files_blueprint.route('', methods=['GET'])
def list_files():
    try:
        files = os.listdir(Config.DATA_FOLDER)  # ✅ Config.DATA_FOLDER is now available
        return jsonify({"files": files}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500  # Improved error handling