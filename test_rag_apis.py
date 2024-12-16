import os
import shutil
import faiss
import logging
from dotenv import load_dotenv  # Import dotenv to load environment variables
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from rag_utils_from_files import create_rag_from_single_file  # Updated to reflect new name
import PyPDF2  # PDF parsing library
from halo import Halo
from prompt_toolkit import prompt
import validators
import requests
import inquirer


# ===========================
# 🔥 Load Environment Variables 🔥
# ===========================
load_dotenv()  # Load environment variables from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Get the API key from the environment

# ===========================
# 🔥 File Paths & Constants 🔥
# ===========================
CURRENT_RAG_PATH = 'data/current_rag_path.txt'
FAISS_INDEX_PATH = 'data/faiss_index'

# ===========================
# 🔥 Logging Configuration 🔥
# ===========================
logging.basicConfig(
    filename='logs/test_results.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_error(message):
    """Prints an error message in red and logs it."""
    red_color = "\033[91m"
    reset_color = "\033[0m"
    print(f"{red_color}❌ {message}{reset_color}")
    logging.error(f"❌ {message}")


def display_response(response, is_error=False):
    """Prints the API response and waits for user input to return to the menu."""
    response_header = "\n🟢 Response:" if not is_error else "\n❌ Error Response:"
    print(response_header)
    print(response)
    print("\nPress ENTER to return to the menu.")
    input()
    clear_screen()


def build_new_rag():
    """Prompt user for a file path to create a new RAG."""
    file_path = input("📂 Enter file path to create new RAG: ").strip()

    # Check if file exists in the destination
    destination_path = os.path.join('data', os.path.basename(file_path))
    if os.path.exists(destination_path):
        overwrite_confirmation = input(f"⚠️ The file already exists at {destination_path}. Do you want to overwrite it? [y/n]: ").strip().lower()
        if overwrite_confirmation != 'y':
            print_error("File not overwritten. Returning to the menu.")
            return

    success = create_rag_from_single_file(
        file_path=file_path, 
        path_to_faiss_index=os.getenv('FAISS_INDEX_PATH'), 
        is_new=True
    )

    if success:
        display_response(f"🟢 New RAG created successfully from the file: {file_path}")
    else:
        print_error("❌ Failed to create new RAG. See logs for more details.")


def test_ask_api():
    """Test the ASK API."""
    query = prompt("❓ Enter your query for the ASK API: ").strip()
    if not query:
        print_error("Query cannot be empty.")
        return

    response = requests.post('http://127.0.0.1:5001/ask', json={'query': query})
    display_response(response.json(), is_error=response.status_code != 200)


def update_rag():
    """Update the RAG with a new URL."""
    url = prompt("🔗 Enter the URL to update the RAG: ").strip()
    if not validators.url(url):
        print_error('Invalid URL format. Please enter a valid URL.')
        return

    response = requests.post('http://127.0.0.1:5001/update-rag/url', json={'url': url})
    display_response(response.json(), is_error=response.status_code != 200)


def check_status():
    """Check the status of the RAG system."""
    response = requests.get('http://127.0.0.1:5001/status')
    display_response(response.json(), is_error=response.status_code != 200)


def display_menu():
    clear_screen()
    questions = [
        inquirer.List(
            'option',
            message="Choose an API to test",
            choices=[
                'Test ASK API', 
                'Update RAG', 
                'Status API', 
                'Build New RAG', 
                'Exit'
            ]
        )
    ]
    answer = inquirer.prompt(questions)

    if answer['option'] == 'Test ASK API':
        test_ask_api()
    elif answer['option'] == 'Update RAG':
        update_rag()
    elif answer['option'] == 'Status API':
        check_status()
    elif answer['option'] == 'Build New RAG':
        build_new_rag()
    elif answer['option'] == 'Exit':
        exit_program()


def exit_program():
    print("👋 Goodbye!")
    logging.info('Exiting the program gracefully.')
    exit(0)


def run_tests():
    try:
        while True:
            display_menu()
    except KeyboardInterrupt:
        exit_program()


if __name__ == '__main__':
    run_tests()