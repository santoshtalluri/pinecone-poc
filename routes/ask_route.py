import logging
import numpy as np
from flask import Blueprint, request, jsonify
from services.embedding_service import get_embedding  # Ensure it uses instructor-xl
from services.pinecone_service import get_pinecone_index
from dotenv import load_dotenv
import os
import openai  # ✅ Import OpenAI for ChatGPT integration

# Load environment variables
load_dotenv()

# Set OpenAI API Key from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY  # ✅ Set the OpenAI API key globally

# Configure logging to log token usage in a separate file
token_log_path = '/Users/santoshtalluri/Documents/MyDevProjects/pinecone-poc/logs/token_usage.log'
logging.basicConfig(
    filename=token_log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

ask_blueprint = Blueprint('ask', __name__)

@ask_blueprint.route('', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        query = data.get('query')
        namespace = os.path.basename(data.get('namespace'))  # ✅ Extract file name as namespace

        if not query:
            logging.error("❌ No query provided.")
            return jsonify({"error": "No query provided"}), 400

        if not namespace:
            logging.error("❌ No namespace provided.")
            return jsonify({"error": "Namespace is required."}), 400

        # Step 1: Generate embedding for the query
        logging.info(f"🧠 Generating embeddings for the query: {query}")
        embedding = get_embedding(query)  # ✅ Ensure this uses Instructor-XL, not MPNet
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()

        # Step 2: Query Pinecone for the most relevant context
        index = get_pinecone_index()
        if not index:
            logging.error("❌ Failed to connect to Pinecone index.")
            return jsonify({"error": "Failed to connect to Pinecone index."}), 500

        logging.info(f"🔍 Querying Pinecone with top_k=10, namespace={namespace}")
        response = index.query(
            vector=embedding,  
            top_k=10,  
            namespace=namespace,
            include_metadata=True  
        )

        matches = response.get('matches', [])
        if not matches:
            logging.warning("⚠️ No matches found in Pinecone for the query.")
            return jsonify({"response": "No relevant information found in the RAG system."}), 200

        # Step 3: Extract relevant content from Pinecone results
        context = ""
        for match in matches:
            metadata = match.get('metadata', {})
            content = metadata.get('content', '')
            context += f"{content}\n\n"

        logging.info(f"🧠 Extracted context from Pinecone (first 500 chars): {context[:500]}...")

        # Step 4: Call OpenAI API to generate a natural language response
        prompt = f"""
You are a smart assistant. The user has asked the following question: '{query}'.
Here is some context related to the question from the RAG system:
{context}
Using this context, provide a clear and natural language response to the user.
"""
        logging.info(f"🧠 Sending context and query to ChatGPT for response generation")

        # Call OpenAI's ChatGPT API (new syntax)
        chatgpt_response = openai.ChatCompletion.create(
            model="gpt-4",  # Use gpt-4 or gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Limit the response length
        )

        answer = chatgpt_response.choices[0].message['content']
        
        # Extract token usage from the OpenAI response
        total_tokens_used = chatgpt_response['usage']['total_tokens']
        logging.info(f"📊 Total tokens used: {total_tokens_used}")
        
        # Append the message about token usage to the user's response
        response_message = f"{answer}\n\nOur program has used {total_tokens_used} tokens to ChatGPT to generate this message."
        
        logging.info(f"🧠 ChatGPT response: {response_message[:200]}...")  # Log first 200 characters of the response

        return jsonify({"response": response_message}), 200

    except Exception as e:
        logging.error(f"❌ Error processing query: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while processing your query."}), 500