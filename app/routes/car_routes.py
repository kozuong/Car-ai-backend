from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from app.config.config import Config
from app.utils.error_handler import with_error_handling, validate_image_file, validate_language
from app.services.gemini_service import GeminiService
from app.services.car_analyzer import CarAnalyzer
from app.utils.cache_manager import CacheManager
from app.utils.image_processor import ImageProcessor
from app.utils.car_utils import get_default_logo, search_logo_url

# Configure logging
logger = logging.getLogger(__name__)

# Initialize services
gemini_service = GeminiService()
car_analyzer = CarAnalyzer()
cache_manager = CacheManager()
image_processor = ImageProcessor()

# Create blueprint
car_bp = Blueprint('car', __name__)

@car_bp.route('/analyze_car', methods=['POST'])
@with_error_handling
def analyze_car():
    logger.info("Received request from app")
    try:
        # Initialize lang at the start of the function
        lang = request.form.get('lang', 'vi')
        validate_language(lang)
        
        # Add request deduplication with detailed logging
        request_id = request.headers.get('X-Request-ID')
        if not request_id:
            request_id = f"req_{datetime.now().timestamp()}"
            logger.info(f"Generated request ID: {request_id}")
        
        logger.info(f"Received request from app with ID: {request_id}, language: {lang}")

        # Check rate limit
        if cache_manager.is_rate_limited(request_id):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': 'Please wait a few seconds before trying again',
                'retry_after': 5
            }), 429

        # Validate image file
        if 'image' not in request.files:
            return jsonify({
                'error': 'Validation error',
                'message': 'No image file provided'
            }), 400
            
        image_file = request.files['image']
        try:
            validate_image_file(image_file)
        except ValidationError as e:
            return jsonify({
                'error': 'Validation error',
                'message': str(e)
            }), 400

        # Process image and analyze car
        base64_image = image_processor.encode_image(image_file)
        if not base64_image:
            return jsonify({
                'error': 'Image processing error',
                'message': 'Image encoding failed'
            }), 400

        brand, logo_crop = image_processor.detect_logo(image_file)
        if brand and brand.lower() != 'unknown':
            logo_url = search_logo_url(brand)
        else:
            logo_url = None

        # Analyze car with Gemini
        content_en = gemini_service.analyze_image(base64_image)
        content_vi = gemini_service.translate_text(content_en)

        # Extract fields
        car_data = car_analyzer.extract_car_data(content_en, content_vi, brand, logo_url)
        
        return jsonify(car_data)

    except Exception as e:
        logger.error(f"Exception in analyze_car: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Processing error',
            'message': f'Error processing image: {str(e)}'
        }), 500

@car_bp.route('/translate_history', methods=['POST'])
@with_error_handling
def translate_history():
    data = request.get_json()
    record = data.get('record', {})
    lang = data.get('lang', 'vi')
    validate_language(lang)

    translated = car_analyzer.translate_car_record(record, lang)
    return jsonify(translated) 