import logging
from flask import Blueprint, request, jsonify
from utilities.pdf_extraction_utility import extract_text_from_url

add_url_blueprint = Blueprint('add_url', __name__)

@add_url_blueprint.route('', methods=['POST'])
def add_url():
    try:
        data = request.get_json()
        url = data.get('url')

        if not url:
            logging.error("❌ URL is missing in the request payload.")
            return jsonify({"error": "URL is required"}), 400

        file_path, error = extract_text_from_url(url)
        if error:
            return jsonify({"error": error}), 400

        return jsonify({"message": f"File created successfully", "file_path": file_path}), 201
    except Exception as e:
        logging.error(f"❌ An unexpected error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500