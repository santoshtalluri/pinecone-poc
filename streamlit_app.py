import streamlit as st
import requests

# Adjust this to the actual base URL and port where your Flask app is running
# If you're running Flask locally on port 5001, use:
API_BASE_URL = "http://127.0.0.1:5001"

def main():
    st.title("PineCone POC - Streamlit UI")
    st.write("Use this page to interact with your Flask endpoints.")

    # Create a dropdown in the sidebar to choose an endpoint to interact with
    endpoints = [
        "ask",
        "add-file",
        "remove-file",
        "list-files",
        "tree-view",
        "add-url",
        "create-new-rag",
        "view-rags",
        "delete-rag",
        "set-default-rag",
        "get-default-rag",
        "health",
        "view-namespace-summary",
    ]
    endpoint_choice = st.sidebar.selectbox("Choose an endpoint", endpoints)

    # Show different UI elements based on the chosen endpoint
    if endpoint_choice == "ask":
        st.subheader("Ask Endpoint")
        question = st.text_input("Enter your question:")
        if st.button("Send Question"):
            # Assuming /ask expects a JSON payload like {"question": "..."}
            payload = {"question": question}
            resp = requests.post(f"{API_BASE_URL}/ask", json=payload)
            st.write("Response:", resp.json())

    elif endpoint_choice == "add-file":
        st.subheader("Add File Endpoint")
        file_path = st.text_input("File path or content location:")
        if st.button("Add File"):
            payload = {"file_path": file_path}
            resp = requests.post(f"{API_BASE_URL}/add-file", json=payload)
            st.write("Response:", resp.json())

    elif endpoint_choice == "remove-file":
        st.subheader("Remove File Endpoint")
        file_name = st.text_input("File name to remove:")
        if st.button("Remove File"):
            # Typically you'd do a DELETE request, but confirm your Flask route
            resp = requests.delete(f"{API_BASE_URL}/remove-file", json={"file_name": file_name})
            st.write("Response:", resp.json())

    elif endpoint_choice == "list-files":
        st.subheader("List Files Endpoint")
        if st.button("List Files"):
            resp = requests.get(f"{API_BASE_URL}/list-files")
            st.write("Response:", resp.json())

    elif endpoint_choice == "tree-view":
        st.subheader("Tree View Endpoint")
        if st.button("Show Tree"):
            # This endpoint is /tree-view/ with a trailing slash
            resp = requests.get(f"{API_BASE_URL}/tree-view/")
            st.write("Response:", resp.text)

    elif endpoint_choice == "add-url":
        st.subheader("Add URL Endpoint")
        url = st.text_input("URL to add:")
        if st.button("Add URL"):
            resp = requests.post(f"{API_BASE_URL}/add-url", json={"url": url})
            st.write("Response:", resp.json())

    # Make sure this `elif` is aligned with the one above
    elif endpoint_choice == "create-new-rag":
        st.subheader("Create New RAG")
        file_path = st.text_input("File Path:")
        rag_name = st.text_input("RAG Name:")
        if st.button("Create RAG"):
            payload = {
                "file_path": file_path,
                "rag_name": rag_name
            }
            resp = requests.post(f"{API_BASE_URL}/create-new-rag", json=payload)
            st.write("Response:", resp.json())

    elif endpoint_choice == "view-rags":
        st.subheader("View RAGs")
        if st.button("View RAGs"):
            resp = requests.get(f"{API_BASE_URL}/view-rags")
            st.write("Response:", resp.json())

    elif endpoint_choice == "delete-rag":
        st.subheader("Delete RAG")
        rag_id = st.text_input("RAG ID to delete:")
        if st.button("Delete RAG"):
            resp = requests.delete(f"{API_BASE_URL}/delete-rag", json={"rag_id": rag_id})
            st.write("Response:", resp.json())

    elif endpoint_choice == "set-default-rag":
        st.subheader("Set Default RAG")
        rag_id = st.text_input("RAG ID to set as default:")
        if st.button("Set Default"):
            resp = requests.post(f"{API_BASE_URL}/set-default-rag", json={"rag_id": rag_id})
            st.write("Response:", resp.json())

    elif endpoint_choice == "get-default-rag":
        st.subheader("Get Default RAG")
        if st.button("Get Default"):
            resp = requests.get(f"{API_BASE_URL}/get-default-rag")
            st.write("Response:", resp.json())

    elif endpoint_choice == "health":
        st.subheader("Health Endpoint")
        if st.button("Check Health"):
            resp = requests.get(f"{API_BASE_URL}/health")
            st.write("Response:", resp.json())

    elif endpoint_choice == "view-namespace-summary":
        st.subheader("View Namespace Summary")
        namespace = st.text_input("Namespace:")
        if st.button("View Summary"):
            # e.g. /view-namespace-summary/<namespace>
            resp = requests.get(f"{API_BASE_URL}/view-namespace-summary/{namespace}")
            st.write("Response:", resp.json())

if __name__ == "__main__":
    main()