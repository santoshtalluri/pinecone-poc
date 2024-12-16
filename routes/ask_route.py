import logging
from flask import Blueprint, request, jsonify

ask_blueprint = Blueprint('ask', __name__)

@ask_blueprint.route('', methods=['POST'])
def ask():
    """
    Ask a question to the RAG system.

    This route takes a query as input and returns an answer 
    based on the content stored in the RAG system.

    Args:
        query (str): The question to ask the RAG.

    Returns:
        JSON: The response from the RAG system.
    """
    try:
        data = request.get_json()
        query = data.get('query')
        
        if query:
            # Simulate RAG system response
            response = "This is a placeholder response"
            return jsonify({"response": response}), 200
        else:
            return jsonify({"error": "No query provided"}), 400
    except Exception as e:
        logging.error(f"❌ Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred"}), 500