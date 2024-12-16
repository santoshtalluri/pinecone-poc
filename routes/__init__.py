from flask import Flask
from routes.ask_route import ask_blueprint
from routes.add_file_route import add_file_blueprint
from routes.remove_file_route import remove_file_blueprint
from routes.list_files_route import list_files_blueprint
from routes.tree_view_route import files_list_blueprint
from routes.add_url_route import add_url_blueprint  
from routes.create_new_rag_route import create_new_rag_blueprint  



def register_blueprints(app: Flask):
    app.register_blueprint(ask_blueprint, url_prefix='/ask')
    app.register_blueprint(add_file_blueprint, url_prefix='/add-file')
    app.register_blueprint(remove_file_blueprint, url_prefix='/remove-file')
    app.register_blueprint(list_files_blueprint, url_prefix='/list-files')
    app.register_blueprint(files_list_blueprint, url_prefix='/tree-view')
    app.register_blueprint(add_url_blueprint, url_prefix='/add-url')  
    app.register_blueprint(create_new_rag_blueprint, url_prefix='/create-new-rag')  
    return app
