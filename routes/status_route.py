from flask import Blueprint, jsonify

status_blueprint = Blueprint('status', __name__)

@status_blueprint.route('', methods=['GET'])
def status():
    return jsonify({
        "status": "RAG system is running",
        "vectors": 1  # Hardcoded for simplicity; update dynamically if needed
    })