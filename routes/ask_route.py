import logging
import requests
from flask import Blueprint, request, jsonify
from services.embedding_service import EmbeddingService, adjust_embedding_dimensions
from services.pinecone_service import get_pinecone_index
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os
import re
import openai
from config import Config
import json

# Load environment variables
load_dotenv()

# Set OpenAI API Key if OpenAI is the selected LLM
if Config.LLM_MODEL == "openai":
    OPENAI_API_KEY = Config.OPENAI_API_KEY
    openai.api_key = OPENAI_API_KEY

# Configure logging for token usage
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
        # Parse request data
        data = request.get_json()
        query = data.get('query')
        namespace = data.get('rag_name')

        if not query:
            logging.error("❌ No query provided.")
            return jsonify({"error": "No query provided"}), 400

        if not namespace:
            logging.error("❌ No namespace provided.")
            return jsonify({"error": "Namespace (rag_name) is required."}), 400

        # Generate query embedding
        logging.info(f"🧠 Generating embedding for query: {query}")
        embedding_service = EmbeddingService()
        embedding = embedding_service.generate_embeddings(query)

        # Adjust embedding dimensions to match Pinecone index
        #embedding = adjust_embedding_dimensions(embedding, Config.PINECONE_INDEX_DIMENSION)

        # Debug raw embedding
        logging.info(f"Generated raw embedding: {embedding}")
        logging.info(f"Generated raw embedding dimensions: {len(embedding)}")

        # Adjust embedding dimensions to match Pinecone index
        logging.info(f"Original embedding dimensions: {len(embedding)}")
        embedding = adjust_embedding_dimensions(embedding, Config.PINECONE_INDEX_DIMENSION)
        logging.info(f"Final embedding sent to Pinecone: {embedding}")
        logging.info(f"Final embedding dimensions: {len(embedding)}")

        if embedding is None or not isinstance(embedding, list):
            logging.error("❌ Failed to generate embedding for the query.")
            return jsonify({"error": "Failed to generate embedding for the query."}), 500

        # Query Pinecone for context
        logging.info(f"🔍 Querying Pinecone with namespace: {namespace}")
        index = get_pinecone_index()
        if index is None:
            logging.error("❌ Pinecone index connection failed.")
            return jsonify({"error": "Failed to connect to Pinecone index."}), 500

        response = index.query(
            vector=embedding,
            top_k=50,
            namespace=namespace,
            include_metadata=True
        )

        # Retrieve matches
        matches = response.get('matches', [])
        if not matches:
            logging.warning("⚠️ No matches found in Pinecone for the query.")
            return jsonify({"response": "No relevant information found in the RAG system."}), 200

        # Re-rank matches dynamically
        context_embeddings = [
            adjust_embedding_dimensions(
                embedding_service.generate_embeddings(match.get('metadata', {}).get('content', '')),
                Config.PINECONE_INDEX_DIMENSION
            ) for match in matches
        ]
        similarities = cosine_similarity([embedding], context_embeddings).flatten()
        adaptive_threshold = max(0.4, similarities.mean() - similarities.std())
        filtered_matches = [
            match for match, similarity in zip(matches, similarities) if similarity >= adaptive_threshold
        ]

        if not filtered_matches:
            logging.warning("⚠️ No high-confidence matches found in the RAG system.")
            return jsonify({"response": "No relevant information found in the RAG system."}), 200

        # Combine context from top-ranked matches
        ranked_matches = sorted(zip(filtered_matches, similarities), key=lambda x: x[1], reverse=True)
        top_contexts = [match[0].get('metadata', {}).get('content', '') for match in ranked_matches[:10]]
        context = "\n\n".join(top_contexts)

        # Log the combined context
        logging.info(f"🔍 Re-ranked context (first 500 chars): {context[:500]}...")

        # Enhanced function to extract amounts near relevant phrases
        def extract_amount(context):
            # Search for key phrases and amounts nearby
            match = re.search(r"(total amount paid|this month's charges|since your last bill).*?\$([\d,]+\.\d{2})", context, re.IGNORECASE)
            if match:
                return match.group(2)
            return None

        # Check if the query specifically asks for the total amount paid
        if "total amount paid" in query.lower():
            amount = extract_amount(context)
            if amount:
                return jsonify({"response": f"The total amount paid is ${amount}."}), 200

        # Generate response using LLM
        if Config.LLM_MODEL == "openai":
            logging.info("🧠 Using OpenAI ChatGPT for response generation.")
            prompt = f"""
            You are a highly intelligent assistant. The user has asked the following question: '{query}'.
            Here is some context retrieved from a document related to the question:
            {context}

            Based on this context, provide a clear and accurate response to the user's question.
            """
            chatgpt_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            answer = chatgpt_response.choices[0].message.content
            total_tokens_used = chatgpt_response['usage']['total_tokens']
            response_message = f"{answer}\n\nThis response used {total_tokens_used} tokens."

        elif Config.LLM_MODEL == "ollama":
            logging.info("🧠 Using Ollama for response generation.")
            if Config.OLLAMA_GENERATION_MODEL is None:
                logging.error("❌ Ollama generation model is not specified in Config.")
                return jsonify({"error": "Ollama generation model is not configured."}), 500

            url = f"{Config.OLLAMA_HOST}/api/generate"
            payload = {
                "model": Config.OLLAMA_GENERATION_MODEL,
                "prompt": f"""
                You are a smart assistant. The user has asked the following question: '{query}'.
                Here is some context related to the question from the RAG system:
                {context}

                Based on this context, provide a clear and detailed response to the user's question.
                """
            }
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(url, json=payload, stream=True)
                if response.status_code != 200:
                    logging.error(f"❌ Ollama API error: {response.text}")
                    return jsonify({"error": "Failed to generate a response using Ollama."}), 500

                full_response = ""
                for line in response.iter_lines(decode_unicode=True):
                    if line.strip():
                        try:
                            parsed_line = json.loads(line)
                            if "response" in parsed_line:
                                full_response += parsed_line["response"]
                            if parsed_line.get("done", False):
                                break
                        except json.JSONDecodeError as e:
                            logging.warning(f"⚠️ Skipping invalid JSON line: {line}. Error: {str(e)}")

                if not full_response.strip():
                    raise ValueError("No valid response generated from Ollama.")

                response_message = full_response.strip()
            except Exception as e:
                logging.error(f"❌ Error processing Ollama's response: {str(e)}", exc_info=True)
                return jsonify({"error": "Failed to parse Ollama's response."}), 500

        else:
            logging.error(f"❌ Unsupported LLM model specified: {Config.LLM_MODEL}")
            return jsonify({"error": f"Unsupported LLM model: {Config.LLM_MODEL}"}), 400

        logging.info(f"🧠 Generated response: {response_message[:200]}...")
        return jsonify({"response": response_message}), 200

    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while processing your query."}), 500