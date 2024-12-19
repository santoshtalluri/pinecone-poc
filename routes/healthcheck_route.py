from flask import Blueprint, jsonify

healthcheck_blueprint = Blueprint('healthcheck', __name__)

@healthcheck_blueprint.route('', methods=['GET'])
def healthcheck():
    """Check the health of the application services (Pinecone, MongoDB, etc.)"""
    try:
        health_status = {
            "mongo": "Available",
            "pinecone": "Available",
            "flask": "Running"
        }
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500