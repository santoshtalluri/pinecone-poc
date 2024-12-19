import os
from pinecone import Pinecone
from dotenv import load_dotenv

# Load .env file and print PINECONE_API_KEY for debugging
load_dotenv()

# Load API Key
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
pc = Pinecone(api_key=PINECONE_API_KEY)

# Connect to index
index = pc.Index('rag-index')

# Query for existing vectors
response = index.query(
    vector=[0.1] * 1536,  # Dummy query vector
    top_k=1,
    include_metadata=True  # ✅ Include metadata in the query
)
print("Response from Pinecone query:")
print(response)