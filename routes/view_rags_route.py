import logging
from flask import Blueprint, jsonify
from pinecone import Pinecone
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get API key and initialize Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=PINECONE_API_KEY)

# Blueprint
view_rags_blueprint = Blueprint('view_rags', __name__)

@view_rags_blueprint.route('', methods=['GET'])
def view_rags():
    """
    View all RAGs stored in Pinecone as indexes and namespaces.
    Each RAG will display:
    - RAG Name (either index name or namespace name)
    - Total Vectors in that RAG
    - Files Used to Create Vectors
    """
    try:
        logging.info("📘 Retrieving available Pinecone indexes...")
        
        # Step 1: List all indexes available in Pinecone
        available_indexes = pc.list_indexes().names()
        rags_info = []

        for index_name in available_indexes:
            try:
                logging.info(f"📘 Retrieving namespace stats for index: {index_name}")
                index = pc.Index(index_name)
                index_stats = index.describe_index_stats()
                
                namespaces = index_stats.get('namespaces', {})
                total_vectors = sum(stats['vector_count'] for stats in namespaces.values())

                for namespace, stats in namespaces.items():
                    file_names = get_file_names_from_pinecone(index, namespace)
                    rags_info.append({
                        "rag_name": f"{index_name}::{namespace}" if namespace else index_name,
                        "index_name": index_name,
                        "namespace": namespace if namespace else "default",
                        "total_vectors": stats['vector_count'],
                        "files_used": file_names  # ✅ Display file names that contributed to this RAG
                    })

            except Exception as e:
                logging.error(f"❌ Error retrieving namespace stats for index {index_name}: {str(e)}", exc_info=True)
                rags_info.append({
                    "rag_name": index_name,
                    "index_name": index_name,
                    "error": f"Failed to retrieve stats for {index_name}"
                })

        return jsonify({"available_rags": rags_info}), 200

    except Exception as e:
        logging.error(f"❌ Error viewing Pinecone RAGs: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


def get_file_names_from_pinecone(index, namespace):
    """
    Query Pinecone to get all file names used in the RAG.
    """
    try:
        logging.info(f"📘 Querying Pinecone for file names in namespace: {namespace}")
        response = index.query(
            vector=[0] * 1536,  # Dummy vector for query
            top_k=1000,  # Return 1000 results
            namespace=namespace,
            include_metadata=True
        )
        
        file_names = set()
        for match in response.get('matches', []):
            metadata = match.get('metadata', {})
            file_name = metadata.get('file_name')
            if file_name:
                file_names.add(file_name)
        
        return list(file_names)
    except Exception as e:
        logging.error(f"❌ Error retrieving file names from Pinecone: {str(e)}", exc_info=True)
        return []