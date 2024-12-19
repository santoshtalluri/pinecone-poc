import os
import logging
from flask import Blueprint, jsonify
from services.pinecone_service import get_pinecone_index
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Blueprint for the /view-namespace-summary route
view_namespace_summary_blueprint = Blueprint('view_namespace_summary', __name__)

@view_namespace_summary_blueprint.route('/<namespace>', methods=['GET'])
def view_namespace_summary(namespace):
    """
    View a summary of the information stored in a specific namespace in Pinecone.
    This includes:
    - Total vectors in the namespace
    - List of files linked to the vectors
    - Section names for each vector
    """
    try:
        logging.info(f"📘 Retrieving summary for namespace: {namespace}")

        # Step 1: Connect to Pinecone
        index = get_pinecone_index()
        if not index:
            logging.error(f"❌ Pinecone index connection failed.")
            return jsonify({"error": "Pinecone index connection failed."}), 500

        logging.info(f"✅ Connected to Pinecone index for namespace: {namespace}")

        # Step 2: Query Pinecone for all vectors in the namespace
        logging.info(f"📡 Querying all vectors in namespace: {namespace}")
        response = index.query(
            vector=[0.001] * 1536,  # Dummy vector for querying
            top_k=1000,  # Get up to 1000 results
            namespace=namespace,
            include_metadata=True
        )

        matches = response.get('matches', [])
        if not matches:
            logging.warning(f"⚠️ No vectors found in namespace: {namespace}")
            return jsonify({"response": "No vectors found in this namespace."}), 200

        # Step 3: Extract metadata for all vectors
        total_vectors = len(matches)
        file_names = set()
        section_names = set()
        vector_metadata = []

        for match in matches:
            metadata = match.get('metadata', {})
            file_name = metadata.get('file_name', 'Unknown File')
            section_name = metadata.get('section_name', 'Unknown Section')
            file_names.add(file_name)
            section_names.add(section_name)

            vector_metadata.append({
                "vector_id": match.get('id', 'No ID'),
                "file_name": file_name,
                "section_name": section_name,
                "rag_name": metadata.get('rag_name', 'Unknown RAG'),
                "content_preview": metadata.get('content', 'No content')[:100]  # Show only the first 100 characters
            })

        # Step 4: Summarize the key details
        summary = {
            "namespace": namespace,
            "total_vectors": total_vectors,
            "files_used": list(file_names),
            "sections_found": list(section_names),
            "sample_vectors": vector_metadata[:5]  # Display the first 5 vector summaries
        }

        logging.info(f"✅ Summary for namespace {namespace}: {summary}")

        return jsonify(summary), 200

    except Exception as e:
        logging.error(f"❌ Error retrieving namespace summary: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while retrieving the namespace summary."}), 500