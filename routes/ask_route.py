import logging  # ✅ Add this import
from flask import Blueprint, request, jsonify
from vector_store_instance import vector_store  # Ensure this import is correct
from langchain.chains import RetrievalQA  # ✅ Import RetrievalQA for full RAG system
from langchain_openai import ChatOpenAI  # ✅ Import ChatOpenAI for LLM responses

ask_blueprint = Blueprint('ask', __name__)

@ask_blueprint.route('', methods=['POST'])
def ask():
    if vector_store is None:
        return jsonify({"error": "RAG system is not initialized"}), 500

    try:
        retriever = vector_store.as_retriever()  # Correctly gets the retriever
        data = request.get_json()
        query = data.get('query', '')

        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Option 1: Simple FAISS document retrieval (comment out one of the options)
        # response = retriever.get_relevant_documents(query)  # ✅ Correct method for FAISS retriever

        # Option 2: Use LLM + FAISS vector store (uncomment the code below to use RetrievalQA)
        rag_system = RetrievalQA.from_chain_type(
            llm=ChatOpenAI(model="gpt-4-turbo"), 
            retriever=retriever
        )
        response = rag_system.run(query)  # ✅ Correct method for RetrievalQA

        return jsonify({"response": response}), 200
    except Exception as e:
        logging.error(f'Error querying RAG system: {str(e)}', exc_info=True)  # Proper logging now
        return jsonify({"error": "Error occurred"}), 500