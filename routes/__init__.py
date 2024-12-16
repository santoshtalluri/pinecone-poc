from flask import Flask
from routes.ask_route import ask_blueprint
from routes.build_rag_route import build_rag_blueprint
from routes.status_route import status_blueprint

def register_blueprints(app: Flask):
    """Register all blueprints to the Flask app."""
    app.register_blueprint(ask_blueprint, url_prefix='/ask')
    app.register_blueprint(build_rag_blueprint, url_prefix='/update-rag/url')
    app.register_blueprint(status_blueprint, url_prefix='/status')
    return app