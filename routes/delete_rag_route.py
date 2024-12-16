import os
import logging
from flask import Blueprint, request, jsonify

delete_rag_blueprint = Blueprint('delete_rag', __name__)

@delete_rag_blueprint.route('', methods=['DELETE'])
def delete_rag():
    """
    Delete a specific RAG from the system.

    Args:
        rag_name (str): The name of the RAG to delete.

    Returns:
        JSON: Success or failure message.
    """
    try:
        data = request.get_json()
        rag_name = data.get('rag_name')

        if rag_name:
            rag_path = os.path.join(Config.FAISS_NEW_RAGS_PATH, rag_name)
            if os.path.exists(rag_path):
                os.rmdir(rag_path)
                return jsonify({"message": f"RAG {rag_name} deleted successfully."}), 200
            else:
                return jsonify({"error": f"RAG {rag_name} not found."}), 404
        else:
            return jsonify({"error": "No RAG name provided"}), 400
    except Exception as e:
        logging.error(f"❌ Error deleting RAG: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500