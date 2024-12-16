import os
import logging
from flask import Blueprint, jsonify
from config import Config  # ✅ Import Config for directory paths

view_rags_blueprint = Blueprint('view_rags', __name__)

@view_rags_blueprint.route('', methods=['GET'])
def view_rags():
    """
    View all RAGs stored in /faiss_index/ and /faiss_index/new_rags/.
    """
    try:
        faiss_index_path = Config.FAISS_INDEX_PATH
        new_rags_path = Config.FAISS_NEW_RAGS_PATH

        # List RAGs in /faiss_index/ (base RAGs)
        base_rags = [
            name for name in os.listdir(faiss_index_path) 
            if os.path.isdir(os.path.join(faiss_index_path, name)) 
            and name not in ['new_rags']  # Exclude the 'new_rags' folder itself
            and not name.startswith('.')  # Exclude hidden folders like .ipynb_checkpoints
            and name == Config.BASE_RAG_NAME  # ✅ Only show the BASE_RAG_NAME
        ]

        # List RAGs in /faiss_index/new_rags/ (newly created RAGs)
        new_rags = [
            name for name in os.listdir(new_rags_path) 
            if os.path.isdir(os.path.join(new_rags_path, name)) 
            and not name.startswith('.')  # Exclude hidden folders like .ipynb_checkpoints
        ]

        logging.info(f"📂 Base RAGs: {base_rags}")
        logging.info(f"📂 New RAGs: {new_rags}")

        return jsonify({
            "base_rags": base_rags,
            "new_rags": new_rags
        }), 200
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred while viewing RAGs: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500