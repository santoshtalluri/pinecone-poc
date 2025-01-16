import requests

# Define the base URL of your RAG system
BASE_URL = "http://localhost:5001"  # Update this with your server's URL

# List of endpoints to test
ENDPOINTS = {
    "Ask API": "/ask",
    "Add File API": "/add-file",
    "Add URL API": "/add-url",
    "Create New RAG API": "/create-new-rag",
    "View RAGs API": "/view-rags",
    "Get Default RAG API": "/get-default-rag"
}

# Payloads for endpoints that require a request body
PAYLOADS = {
    "/ask": {"query": "What is RAG?", "namespace": "VerifyRAG"},
    "/add-file": {
        "file_path": "/Users/santoshtalluri/Documents/MyDevProjects/pinecone-poc/data/Santosh.pdf",
        "rag_name": "VerifyRAG"
    },
    "/add-url": {
        "url": "https://www.google.com/about/careers/applications/jobs/results/128510769372242630-group-product-manager-ads",
        "rag_name": "VerifyRAG"
    },
    "/create-new-rag": {
        "folder_path": "/Users/santoshtalluri/Documents/MyDevProjects/pinecone-poc/data/Santosh.pdf"
    }
}

# Function to test an endpoint
def test_endpoint(endpoint_name, path):
    url = f"{BASE_URL}{path}"
    payload = PAYLOADS.get(path, {})
    
    try:
        # Determine request method based on payload presence
        if payload:
            response = requests.post(url, json=payload)
        else:
            response = requests.get(url)
        
        # Print result
        if response.status_code == 200:
            print(f"[PASS] {endpoint_name}: {response.status_code}")
        else:
            print(f"[FAIL] {endpoint_name}: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"[ERROR] {endpoint_name}: {e}")

# Main function to test all endpoints
def main():
    print("Testing RAG system endpoints...\n")
    for endpoint_name, path in ENDPOINTS.items():
        test_endpoint(endpoint_name, path)

if __name__ == "__main__":
    main()