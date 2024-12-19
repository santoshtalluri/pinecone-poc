from flask import Flask
from routes.ask_route import ask_blueprint
from routes.add_file_route import add_file_blueprint
from routes.remove_file_route import remove_file_blueprint
from routes.list_files_route import list_files_blueprint
from routes.tree_view_route import files_list_blueprint
from routes.add_url_route import add_url_blueprint  
from routes.create_new_rag_route import create_new_rag_blueprint  
from routes.view_rags_route import view_rags_blueprint
from routes.delete_rag_route import delete_rag_blueprint
from routes.set_default_rag_route import set_default_rag_blueprint
from routes.get_default_rag_route import get_default_rag_blueprint
from routes.healthcheck_route import healthcheck_blueprint
from routes.namespace_summary import view_namespace_summary_blueprint


def register_blueprints(app: Flask):
    """
    Register all routes (blueprints) with the Flask app.

    Args:
        app (Flask): The Flask application instance.
    
    Returns:
        Flask: The Flask app with all routes registered.
    """
    app.register_blueprint(ask_blueprint, url_prefix='/ask')
    app.register_blueprint(add_file_blueprint, url_prefix='/add-file')
    app.register_blueprint(remove_file_blueprint, url_prefix='/remove-file')
    app.register_blueprint(list_files_blueprint, url_prefix='/list-files')
    app.register_blueprint(files_list_blueprint, url_prefix='/tree-view')
    app.register_blueprint(add_url_blueprint, url_prefix='/add-url')  
    app.register_blueprint(create_new_rag_blueprint, url_prefix='/create-new-rag')  
    app.register_blueprint(view_rags_blueprint, url_prefix='/view-rags') 
    app.register_blueprint(delete_rag_blueprint, url_prefix='/delete-rag') 
    app.register_blueprint(set_default_rag_blueprint, url_prefix='/set-default-rag')
    app.register_blueprint(get_default_rag_blueprint, url_prefix='/get-default-rag')
    app.register_blueprint(healthcheck_blueprint, url_prefix='/health')
    app.register_blueprint(view_namespace_summary_blueprint, url_prefix='/view-namespace-summary')
    return app
