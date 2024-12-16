import requests
import logging
from bs4 import BeautifulSoup
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.schema import Document

def update_rag_system_with_url(url, vector_store):
    try:
        logging.info(f'🌐 Valid URL received: {url}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.get_text(separator=' ', strip=True)
        
        documents = [Document(page_content=content, metadata={"source": url})]
        vector_store.add_documents(documents)
        
        logging.info(f'✅ Successfully added content from URL to the RAG system.')
        return True
    except Exception as e:
        logging.error(f'❌ Error updating RAG system from URL: {str(e)}', exc_info=True)
    return False

def query_rag(rag_system, query_text):
    try:
        response = rag_system.run(query_text)
        logging.info(f'✅ Query successful. Response: {response}')
        return response
    except Exception as e:
        logging.error(f'❌ Error querying RAG system: {str(e)}', exc_info=True)
        return 'An error occurred while querying the RAG system.'
    
def extract_content_from_url(url):
    """Extract content from a URL."""
    try:
        logging.info(f'🌐 Fetching content from URL: {url}')
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted tags like <script>, <style>, etc.
        for tag in soup(['script', 'style', 'noscript', 'iframe']):
            tag.decompose()

        content = soup.get_text(separator=' ', strip=True)
        
        if not content.strip():
            logging.warning(f'⚠️ No visible content extracted from URL: {url}')
            return None

        logging.info(f'✅ Successfully extracted content from URL (first 500 chars): {content[:500]}')
        return content

    except requests.exceptions.RequestException as e:
        logging.error(f'❌ Error fetching URL: {url}. Error: {str(e)}')
        return None
    except Exception as e:
        logging.error(f'❌ Unexpected error while extracting URL content: {str(e)}', exc_info=True)
        return None
    
    