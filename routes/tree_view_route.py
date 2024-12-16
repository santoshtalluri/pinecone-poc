import os
from flask import Blueprint, jsonify
from config import Config

files_list_blueprint = Blueprint('list_view', __name__)

@files_list_blueprint.route('/', methods=['GET'])
def view_tree():
    file_tree = {}
    for root, dirs, files in os.walk(Config.DATA_FOLDER):
        relative_path = os.path.relpath(root, Config.BASE_DIR)
        file_tree[relative_path] = files
    return jsonify(file_tree)