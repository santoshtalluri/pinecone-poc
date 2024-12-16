import requests
from flask import Blueprint, jsonify

health_blueprint = Blueprint('health', __name__)

@health_blueprint.route('', methods=['GET'])
def health_check():
    """
    Health check for all routes.

    Calls each registered route and returns their status (200 OK or error).
    
    Returns:
        JSON: Status of all routes.
    """
    routes = [
        "/add-file",
        "/add-url",
        "/ask",
        "/create-new-rag",
        "/delete-rag",
        "/get-default-rag",
        "/list-files",
        "/tree-view",
        "/remove-file",
        "/set-default-rag",
        "/view-rags"
    ]

    results = {}
    for route in routes:
        try:
            response = requests.get(f"http://127.0.0.1:5001{route}")
            status_code = response.status_code
            if status_code == 200:
                results[route] = "✅ UP (200 OK)"
            else:
                results[route] = f"⚠️ DOWN ({status_code})"
        except Exception as e:
            results[route] = f"❌ ERROR ({str(e)})"

    return jsonify(results)