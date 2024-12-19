import os
import logging
import re  # ✅ Added re to use clean_text function
from flask import Blueprint, request, jsonify
from services.pinecone_service import get_pinecone_index
from utilities.pdf_extraction_utility import extract_text_from_pdf
from services.embedding_service import get_embedding  # ✅ Uses dynamic embedding selection
from dotenv import load_dotenv
import pinecone  # ✅ Import pinecone to delete/recreate index

# Load environment variables
load_dotenv()

create_new_rag_blueprint = Blueprint('create_new_rag', __name__)

def clean_text(text):
    """Clean unwanted headers, footers, and page numbers from the extracted text."""
    text = re.sub(r'P\s*a\s*g\s*e\s*\d+\s*\|\s*\d+', '', text)  # Remove page numbers
    text = re.sub(r'\n+', '\n', text)  # Remove extra newlines
    text = re.sub(r'\s+', ' ', text)  # Remove excessive whitespace
    return text.strip()

def recreate_pinecone_index(index_name, dimension):
    """Recreate the Pinecone index with the correct dimension."""
    try:
        logging.info(f"🗑️ Deleting existing Pinecone index: {index_name}")
        pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment="us-east1-gcp")
        
        # Delete existing index
        try:
            pinecone.delete_index(index_name)
        except Exception as e:
            logging.warning(f"⚠️ Failed to delete existing index. It may not exist. {str(e)}")
        
        logging.info(f"📦 Recreating Pinecone index '{index_name}' with dimension {dimension}")
        pinecone.create_index(index_name, dimension=dimension, metric="cosine")

        logging.info(f"✅ Successfully created index '{index_name}' with dimension {dimension}")
    except Exception as e:
        logging.error(f"❌ Error recreating Pinecone index: {str(e)}", exc_info=True)
        raise


@create_new_rag_blueprint.route('', methods=['POST'])
def create_new_rag():
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        rag_name = data.get('rag_name')

        if not file_path or not os.path.isfile(file_path):
            logging.error(f"❌ Invalid file path provided: {file_path}")
            return jsonify({"error": "Invalid file path provided."}), 400

        logging.info(f"📄 Starting to process file: {file_path} for RAG: {rag_name}")

        # Step 1: Extract the full text from the PDF file
        full_text = extract_text_from_pdf(file_path)
        if not full_text.strip():
            logging.warning(f"⚠️ No content extracted from {file_path}.")
            return jsonify({"error": "No content extracted from the PDF file."}), 400

        # Step 2: Clean the extracted text
        full_text = clean_text(full_text)
        logging.info(f"📄 Cleaned text from PDF (first 200 chars): {full_text[:200]}...")

        # Step 3: Connect to Pinecone
        index = get_pinecone_index()
        if not index:
            logging.error("❌ Pinecone index connection failed.")
            return jsonify({"error": "Pinecone index connection failed."}), 500

        # Step 4: Generate a single embedding for the entire content
        logging.info(f"🧠 Generating embeddings for the full content of {file_path}")
        embedding = get_embedding(full_text)
        if embedding is None:
            logging.error(f"❌ Failed to generate embedding for the file: {file_path}")
            return jsonify({"error": "Failed to generate embedding for the file."}), 500

        # Step 5: Create a single vector for the entire file
        file_name = os.path.basename(file_path)  # ✅ Use only the file name for namespace
        vector_id = f"{file_name}-full"
        vectors = [{
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "file_name": file_name,
                "rag_name": rag_name,
                "content": full_text  # ✅ Store the full content
            }
        }]

        try:
            logging.info(f"📤 Upserting 1 vector to Pinecone for namespace: {file_name}")
            index.upsert(vectors=vectors, namespace=file_name)

        except pinecone.PineconeApiException as e:
            if "Vector dimension" in str(e) and "does not match" in str(e):
                logging.warning("⚠️ Detected vector dimension mismatch with Pinecone index.")
                
                # Extract the current and expected dimensions from the error message
                import re
                match = re.search(r"Vector dimension (\d+) does not match the dimension of the index (\d+)", str(e))
                if match:
                    current_dim = int(match.group(1))
                    index_dim = int(match.group(2))
                    logging.warning(f"❌ Current embedding dimension: {current_dim}, Pinecone index dimension: {index_dim}")
                    
                    user_input = input(f"⚠️ The current embedding dimension ({current_dim}) does not match the Pinecone index dimension ({index_dim}).\n"
                                       f"Do you want to recreate the index with dimension {current_dim}? (yes/no): ")
                    if user_input.lower() in ['yes', 'y']:
                        recreate_pinecone_index(index_name="rag-index", dimension=current_dim)
                        logging.info("📤 Retrying upsert after index recreation")
                        index.upsert(vectors=vectors, namespace=file_name)
                    else:
                        logging.error("❌ User chose not to recreate the index.")
                        return jsonify({"error": "User declined to recreate the Pinecone index."}), 400
                else:
                    logging.error(f"❌ Could not extract dimensions from error message: {str(e)}")
                    raise

        return jsonify({
            "message": f"RAG '{rag_name}' created successfully.",
            "file_name": file_name,
            "total_vectors": 1
        }), 200

    except Exception as e:
        logging.error(f"❌ Error creating RAG: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while creating the RAG."}), 500