import logging  # ✅ Add this import
from flask import Blueprint, request, jsonify
from vector_store_instance import vector_store  # Ensure this import is correct

ask_blueprint = Blueprint('ask', __name__)

@ask_blueprint.route('/', methods=['POST'])
def ask():
    if vector_store is None:
        return jsonify({"error": "RAG system is not initialized"}), 500

    try:
        retriever = vector_store.as_retriever()  # Correctly gets the retriever
        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({"error": "Query is required"}), 400

        # This line has changed
        response = retriever.get_relevant_documents(query)  # ✅ Correct method for retriever
        return jsonify({"response": response}), 200
    except Exception as e:
        logging.error(f'Error querying RAG system: {str(e)}', exc_info=True)  # Proper logging now
        return jsonify({"error": "Error occurred"}), 500