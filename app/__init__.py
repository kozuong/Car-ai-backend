"""
Car AI Backend Application
"""
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, static_url_path='/static')
    CORS(app)  # Enable CORS for all routes
    
    # Import routes
    from app.routes import main
    app.register_blueprint(main.bp)
    
    return app 