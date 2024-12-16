import os
import logging
from flask import Blueprint, request, jsonify

add_url_blueprint = Blueprint('add_url', __name__)

@add_url_blueprint.route('', methods=['POST'])
def add_url():
    """
    Extracts and adds content from a URL to the RAG system.

    Args:
        url (str): The URL to extract content from.

    Returns:
        JSON: Success or failure message.
    """
    try:
        data = request.get_json()
        url = data.get('url')
        
        if url:
            # Extract content from URL (mock implementation)
            logging.info(f"🔗 Extracting content from URL: {url}")
            extracted_content = "Sample content from the URL"
            return jsonify({"message": "URL content added successfully"}), 200
        else:
            return jsonify({"error": "No URL provided"}), 400
    except Exception as e:
        logging.error(f"❌ Error extracting content from URL: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500