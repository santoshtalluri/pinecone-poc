from flask import Blueprint, request, jsonify
from vector_store_instance import vector_store
from rag import extract_content_from_url
from langchain.schema import Document
import logging

build_rag_blueprint = Blueprint('build_rag', __name__)

@build_rag_blueprint.route('', methods=['POST'])
def build_rag_from_url():
    """Update the RAG system with content from a URL."""
    data = request.get_json()
    url = data.get('url', '')

    if not url:
        logging.error('❌ URL is required but not provided.')
        return jsonify({"error": "URL is required"}), 400

    try:
        logging.info(f'🌐 Received URL to update RAG: {url}')
        
        if vector_store is None:
            logging.error('❌ vector_store is None. Cannot update the RAG system.')
            return jsonify({"error": "Internal server error. RAG system is not available."}), 500

        extracted_content = extract_content_from_url(url)
        if extracted_content:
            logging.info(f'📜 Extracted content (first 500 chars): {extracted_content[:500]}')
            
            document = Document(page_content=extracted_content, metadata={"source": url})
            vector_store.add_documents([document])

            logging.info(f'✅ Successfully updated the RAG system with URL: {url}')
            return jsonify({"message": "RAG system updated successfully!"}), 200
        else:
            logging.error(f'⚠️ No content extracted from the URL: {url}')
            return jsonify({"error": "Failed to extract content from URL"}), 500

    except Exception as e:
        logging.error(f'❌ Error updating RAG system with URL: {str(e)}', exc_info=True)
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500