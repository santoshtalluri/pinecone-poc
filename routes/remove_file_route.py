import logging
from flask import Blueprint, request, jsonify
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
pc = Pinecone(api_key=PINECONE_API_KEY)
#index = pc.Index(PINECONE_INDEX_NAME)

# Blueprint
remove_file_blueprint = Blueprint('remove_file', __name__)

@remove_file_blueprint.route('', methods=['DELETE'])
def remove_file():
    """Remove vectors from Pinecone."""
    try:
        data = request.get_json()
        file_id = data.get('file_id')

        # Delete vectors
        response = index.delete(ids=[file_id])
        logging.info(f"✅ File '{file_id}' removed from Pinecone.")
        return jsonify({"message": f"File '{file_id}' removed successfully."}), 200
    except Exception as e:
        logging.error(f"❌ Error removing file: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500