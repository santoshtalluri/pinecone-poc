from flask import Blueprint, request, jsonify
from vector_store_instance import rag_system
import logging

ask_blueprint = Blueprint('ask', __name__)

@ask_blueprint.route('', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('query', '')

    if not query:
        return jsonify({"error": "Query is required"}), 400

    try:
        response = rag_system.run(query)
        return jsonify({"response": response}), 200
    except Exception as e:
        logging.error(f'❌ Error querying RAG system: {str(e)}')
        return jsonify({"error": "Error occurred"}), 500