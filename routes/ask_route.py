import os
import logging
from flask import Blueprint, request, jsonify
from services.pinecone_service import get_pinecone_index
from services.embedding_service import EmbeddingService
from config import Config
from dotenv import load_dotenv
import openai
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity

# Load environment variables
load_dotenv()

ask_blueprint = Blueprint('ask', __name__)

DEFAULT_RAG_FILE = "/Users/santoshtalluri/Documents/MyDevProjects/pinecone-poc/default_rag.txt"

def get_default_rag():
    """
    Retrieve the current default RAG from the default_rag.txt file.
    """
    try:
        if os.path.exists(DEFAULT_RAG_FILE):
            with open(DEFAULT_RAG_FILE, "r") as f:
                return f.read().strip()
        return None
    except Exception as e:
        logging.error(f"❌ Error reading default RAG: {str(e)}")
        return None

def sanitize_query_with_chatgpt(query):
    """
    Use ChatGPT API to sanitize the query.
    """
    try:
        openai.api_key = Config.OPENAI_API_KEY
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sanitize the following query for accurate information retrieval."},
                {"role": "user", "content": query}
            ],
            max_tokens=400
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logging.error(f"❌ Error sanitizing query with ChatGPT API: {str(e)}")
        raise

def advanced_chunking(text, chunk_size=512, overlap=50):
    """
    Chunk text into overlapping segments using sentence boundaries.
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        if current_length + len(sentence) > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-overlap:]  # Retain overlap
            current_length = sum(len(s) for s in current_chunk)
        current_chunk.append(sentence)
        current_length += len(sentence)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def rerank_documents(query_embedding, documents):
    """
    Rerank documents based on cosine similarity to the query embedding.
    """
    for doc in documents:
        doc_vector = doc['metadata'].get('vector', [])  # Assume vector is stored in metadata
        doc['similarity'] = cosine_similarity([query_embedding], [doc_vector])[0][0] if doc_vector else 0
    return sorted(documents, key=lambda x: x['similarity'], reverse=True)

# Initialize EmbeddingService
embedding_service = EmbeddingService()

def sanitize_and_embed_query(query):
    """
    Sanitize the query using ChatGPT API and generate its embedding.
    """
    try:
        # Sanitize query with ChatGPT
        sanitized_query = sanitize_query_with_chatgpt(query)
        logging.info(f"✅ Sanitized query: {sanitized_query}")

        # Generate embedding for sanitized query
        query_embedding = embedding_service.generate_embeddings(sanitized_query)
        logging.info(f"✅ Generated query embedding.")
        return query_embedding
    except Exception as e:
        logging.error(f"❌ Error sanitizing or embedding query: {str(e)}")
        raise

@ask_blueprint.route('', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        query = data.get('query')

        if not query:
            logging.error("❌ Query is missing from the request payload.")
            return jsonify({"error": "Query is required."}), 400

        # Sanitize and embed the query
        query_embedding = sanitize_and_embed_query(query)

        # Initialize Pinecone index
        rag_name = get_default_rag()
        index = get_pinecone_index(index_name=rag_name)
        if not index:
            logging.error(f"❌ Failed to retrieve the Pinecone index: {rag_name}")
            return jsonify({"error": f"Index '{rag_name}' not found."}), 404

        # Query across all namespaces
        logging.info(f"🔍 Querying Pinecone index: {rag_name} across all namespaces.")
        index_stats = index.describe_index_stats()
        namespaces = index_stats.get("namespaces", {}).keys()

        if not namespaces:
            logging.warning("⚠️ No namespaces found in the index.")
            return jsonify({
                "response": "No relevant information found in the index.",
                "rag_name": rag_name,
                "tokens_used": 0
            }), 200

        all_matches = []
        for namespace in namespaces:
            logging.info(f"🔍 Querying namespace: {namespace}")
            search_results = index.query(
                vector=query_embedding,
                top_k=5,  # Adjust as needed
                include_metadata=True,
                namespace=namespace
            )
            matches = search_results.get('matches', [])
            logging.info(f"Matches for namespace {namespace}: {matches}")
            all_matches.extend(matches)

        # Log all retrieved matches
        logging.info(f"All matches retrieved: {all_matches}")

        # Evaluate retrieved documents
        relevant_docs = [doc for doc in all_matches if doc['score'] >= 0.3]  # Reduced threshold
        if not relevant_docs:
            logging.warning("⚠️ No documents matched the query.")
            return jsonify({
                "response": "No relevant information found. Please refine your query.",
                "rag_name": rag_name,
                "tokens_used": 0
            }), 200

        # Rerank retrieved documents
        reranked_docs = rerank_documents(query_embedding, relevant_docs)

        # Format results with more detail
        formatted_matches = [
            {
                "file_name": match['metadata'].get('file_name', 'Unknown File'),
                "content_snippet": match['metadata'].get('content', 'No content available'),
                "score": match['score']
            }
            for match in reranked_docs
        ]

        consolidated_content = "\n\n".join(
            f"File: {match['file_name']}\n"
            f"Content Snippet: {match['content_snippet']}\n"
            f"Relevance Score: {match['score']}"
            for match in formatted_matches
        )

        chatgpt_prompt = (
            f"Sanitized Query: {query}\n\n"
            "The following are the top matches for this query, retrieved from multiple namespaces and files:\n"
            f"{consolidated_content}\n\n"
            "Generate a detailed response summarizing the relevant information. Ensure the response is concise and user-friendly."
        )

        # Pass the prompt to ChatGPT
        logging.info("🤖 Generating response using ChatGPT.")
        chatgpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate a detailed and user-friendly response based on the input."},
                {"role": "user", "content": chatgpt_prompt}
            ],
            max_tokens=1000
        )
        final_response = chatgpt_response['choices'][0]['message']['content'].strip()
        tokens_used = chatgpt_response['usage']['total_tokens']

        logging.info(f"✅ Final Response: {final_response}")
        logging.info(f"🔢 Tokens used: {tokens_used}")

        return jsonify({
            "response": final_response,
            "rag_name": rag_name,
            "tokens_used": tokens_used
        }), 200

    except Exception as e:
        logging.error(f"❌ Error in ask endpoint: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred."}), 500
