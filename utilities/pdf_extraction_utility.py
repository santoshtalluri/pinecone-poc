import os
import logging
import re
import requests
from bs4 import BeautifulSoup  # For parsing webpage content
from PyPDF2 import PdfReader  # For extracting text from PDF files
from config import Config  # For paths like DATA_FOLDER

def extract_text_from_url(url):
    """
    Extract content from a URL (can be a webpage or PDF) and save it as a text file.
    The extracted content is stored in /data/extracted_from_url/{domain-name}/{filename}.txt
    """
    try:
        logging.info(f"🌐 Extracting content from URL: {url}")
        
        # 🌐 Step 1: Get the content from the URL
        response = requests.get(url, timeout=15, stream=True)
        if response.status_code != 200:
            logging.error(f"❌ Failed to fetch URL: {url}, Status code: {response.status_code}")
            return None, f"Failed to fetch URL. Status code: {response.status_code}"

        # Determine if URL points to a PDF file
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' in content_type:
            logging.info(f"📄 URL is a PDF file: {url}")
            content = extract_text_from_pdf_url(response.content, url)
        else:
            logging.info(f"🌐 URL is a webpage: {url}")
            content = extract_text_from_webpage(response.text, url)

        if not content:
            logging.warning(f"⚠️ No content extracted from URL: {url}")
            return None, "No content could be extracted from the URL."

        # 📁 Step 2: Create the /data/extracted_from_url/ directory
        extracted_folder = os.path.join(Config.DATA_FOLDER, 'extracted_from_url')
        os.makedirs(extracted_folder, exist_ok=True)

        # Create a subfolder for each URL
        domain_name = re.sub(r'[^\w]', '_', url.split('//')[-1].split('/')[0])  # Extract domain
        unique_folder_name = f"{domain_name}_{int(os.path.getmtime(__file__))}"
        url_extracted_folder = os.path.join(extracted_folder, unique_folder_name)
        os.makedirs(url_extracted_folder, exist_ok=True)

        filename = f"{domain_name}.txt"
        file_path = os.path.join(url_extracted_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

        logging.info(f"✅ Extracted content from {url} and saved to {file_path}")
        return file_path, None
    except Exception as e:
        logging.error(f"❌ Unexpected error while extracting URL content: {str(e)}", exc_info=True)
        return None, f"An unexpected error occurred: {str(e)}"

def extract_text_from_pdf_url(pdf_content, url):
    """
    Extracts text from a PDF file provided as binary content.
    """
    try:
        reader = PdfReader(pdf_content)
        content = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
        return content
    except Exception as e:
        logging.error(f"❌ Error extracting text from PDF URL: {url}, Error: {str(e)}", exc_info=True)
        return None

def extract_text_from_webpage(html_content, url):
    """
    Extracts and sanitizes text content from a webpage (HTML).
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script, style, noscript, and iframe tags
        for tag in soup(['script', 'style', 'noscript', 'iframe']):
            tag.decompose()

        content = soup.get_text(separator=' ', strip=True)
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    except Exception as e:
        logging.error(f"❌ Error extracting text from webpage URL: {url}, Error: {str(e)}", exc_info=True)
        return None
    
def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        content = ''.join(page.extract_text() for page in reader.pages if page.extract_text())
        if not content.strip():
            logging.warning(f'⚠️ No text extracted from PDF {file_path}. It may be an image-based PDF.')
        return content
    except Exception as e:
        logging.error(f'❌ Error extracting text from PDF {file_path}: {str(e)}', exc_info=True)
        return ''