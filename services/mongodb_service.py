import os
import logging
from pymongo import MongoClient

def get_mongodb_connection():
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        if not mongo_uri:
            raise ValueError("❌ MONGO_URI is not set in .env")

        client = MongoClient(mongo_uri)
        logging.info("✅ Successfully connected to MongoDB.")

        database_name = os.getenv('MONGO_DB_NAME', 'rag_db')
        db = client[database_name]
        logging.info(f"✅ Using MongoDB database: '{database_name}'")

        return client, db
    
    except Exception as e:
        logging.error(f"❌ Error connecting to MongoDB: {str(e)}", exc_info=True)
        return None, None