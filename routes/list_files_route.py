import logging
from flask import Blueprint, request, jsonify
from services.pinecone_service import get_pinecone_index
from config import Config

list_files_blueprint = Blueprint('list_files', __name__)

@list_files_blueprint.route('', methods=['GET'])
def list_files():
    try:
        # Parse namespace (RAG name) from the request
        namespace = request.args.get('rag_name')
        if not namespace:
            logging.error("❌ No namespace provided.")
            return jsonify({"error": "Namespace (rag_name) is required."}), 400

        # Connect to Pinecone
        logging.info(f"🔍 Connecting to Pinecone for namespace: {namespace}")
        index = get_pinecone_index()
        if not index:
            logging.error("❌ Failed to connect to Pinecone index.")
            return jsonify({"error": "Failed to connect to Pinecone index."}), 500

        # Query Pinecone to fetch all metadata for the specified namespace
        logging.info(f"📋 Fetching metadata for namespace: {namespace}")
        try:
            metadata_query = index.query(
                vector=[0] * Config.PINECONE_INDEX_DIMENSION,  # Dummy vector for metadata fetch
                namespace=namespace,
                top_k=1,
                include_metadata=True
            )
        except Exception as e:
            logging.error(f"❌ Error fetching metadata from Pinecone: {str(e)}", exc_info=True)
            return jsonify({"error": "Failed to fetch metadata from Pinecone."}), 500

        # Extract file names from the metadata
        file_names = set()
        for match in metadata_query.get('matches', []):
            metadata = match.get('metadata', {})
            file_name = metadata.get('file_name')
            if file_name:
                file_names.add(file_name)

        # Return the list of unique file names
        logging.info(f"📂 Files used in RAG '{namespace}': {file_names}")
        return jsonify({"rag_name": namespace, "files": list(file_names)}), 200

    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500