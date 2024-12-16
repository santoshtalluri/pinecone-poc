import logging
from flask import Flask
from config import Config
from utils import setup_logging
from routes import register_blueprints

# 📝 Set up logging first to capture all logs
setup_logging(Config.LOG_FILE_PATH, Config.LOGGING_LEVEL)

# Initialize the Flask app
app = Flask(__name__)

# Register routes (Blueprints)
app = register_blueprints(app)

# 🔥 Print all routes after they are registered
with app.app_context():
    logging.info("🔍 Here are all the registered routes:")
    for rule in app.url_map.iter_rules():
        logging.info(f"Endpoint: {rule.endpoint}, Methods: {rule.methods}, URL: {rule.rule}")

if __name__ == "__main__":
    logging.info("📢 Starting Flask server...")
    app.run(host=Config.API_HOST, port=Config.API_PORT, debug=True)