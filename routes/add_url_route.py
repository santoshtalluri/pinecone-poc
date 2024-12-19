import logging
import requests
from flask import Blueprint, request, jsonify
from langchain_community.embeddings import OpenAIEmbeddings
from pinecone import Pinecone
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Blueprint
add_url_blueprint = Blueprint('add_url', __name__)

@add_url_blueprint.route('', methods=['POST'])
def add_url():
    """Add URL content to Pinecone."""
    try:
        data = request.get_json()
        url = data.get('url')

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Generate embeddings
        embeddings = OpenAIEmbeddings()
        vector_data = embeddings.embed_documents([text])

        # Upload to Pinecone
        response = index.upsert(vectors=[{"id": url, "values": vector_data[0]}])
        logging.info(f"✅ URL {url} content added to Pinecone.")
        return jsonify({"message": f"URL '{url}' added successfully."}), 200
    except Exception as e:
        logging.error(f"❌ Error adding URL: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500