from flask import Blueprint, request, jsonify
from app.utils.error_handler import with_error_handling
from app.services.gemini_service import GeminiService
from app.services.car_analyzer import CarAnalyzer
from app.utils.image_processor import ImageProcessor
from app.utils.cache_manager import CacheManager
from app.services.google_custom_search_service import GoogleCustomSearchService
from app.config.translations import get_translation
from app.utils.car_utils import get_default_logo, average_year, average_price
import logging
import sys
from PIL import Image
import io
import re
import time
import copy
from concurrent.futures import ThreadPoolExecutor

bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

# Initialize services
image_processor = ImageProcessor()
gemini_service = GeminiService()
car_analyzer = CarAnalyzer()
cache_manager = CacheManager()
google_search_service = GoogleCustomSearchService()

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@bp.route('/test_api', methods=['GET'])
def test_api():
    return jsonify({"status": "ok", "message": "API is working"})

@bp.route('/test_logo_search', methods=['GET'])
def test_logo_search():
    try:
        result = google_search_service.search_car_logo("Ferrari")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/test_number_produced', methods=['GET'])
def test_number_produced():
    try:
        result = google_search_service.search_number_produced("Ferrari F40")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/translate_history', methods=['POST'])
@with_error_handling
def translate_history():
    # Move the translate_history route logic here
    pass 