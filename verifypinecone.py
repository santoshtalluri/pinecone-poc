import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Load .env file and print PINECONE_API_KEY for debugging
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    print("❌ Error: PINECONE_API_KEY is not set.")
    exit(1)
else:
    print(f"✅ API Key loaded successfully: {PINECONE_API_KEY[:5]}*****")

try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    print(f"✅ Successfully connected to Pinecone using API key.")

    # Check if the index exists, if not, create it
    if 'rag-index' not in pc.list_indexes().names():
        print(f"📢 Index 'rag-index' not found. Creating it now...")
        pc.create_index(
            name='rag-index', 
            dimension=1536, 
            metric='cosine', 
            spec=ServerlessSpec(
                cloud='aws', 
                region='us-west-2'
            )
        )

    # Connect to the Pinecone index
    index = pc.Index('rag-index')
    print(f"✅ Successfully connected to Pinecone index: 'rag-index'")

except Exception as e:
    print(f"❌ Error initializing Pinecone: {str(e)}")