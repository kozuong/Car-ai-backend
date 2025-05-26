from flask import Blueprint, request, jsonify
from app.utils.error_handler import with_error_handling
from app.services.gemini_service import GeminiService
from app.services.car_analyzer import CarAnalyzer
from app.utils.image_processor import ImageProcessor
from app.utils.cache_manager import CacheManager

bp = Blueprint('main', __name__)

# Initialize services
image_processor = ImageProcessor()
gemini_service = GeminiService()
car_analyzer = CarAnalyzer()
cache_manager = CacheManager()

@bp.route('/analyze_car', methods=['POST'])
@with_error_handling
def analyze_car():
    # Move the analyze_car route logic here
    pass

@bp.route('/test_api', methods=['GET'])
def test_api():
    return jsonify({"status": "ok", "message": "API is working"})

@bp.route('/translate_history', methods=['POST'])
@with_error_handling
def translate_history():
    # Move the translate_history route logic here
    pass 