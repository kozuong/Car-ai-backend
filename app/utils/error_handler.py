from functools import wraps
from flask import jsonify, request
import logging
from typing import Dict, Any, Callable
from app.config.translations import get_translation
from traceback import format_exc

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors"""
    def __init__(self, message: str, status_code: int = 400, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ImageProcessingError(APIError):
    """Error during image processing"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, 400, details)

class ExternalAPIError(APIError):
    """Error from external API call"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, 502, details)

class ValidationError(APIError):
    """Error during input validation"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, 400, details)

def handle_api_error(error: APIError) -> tuple[Dict[str, Any], int]:
    """Convert APIError to JSON response"""
    response = {
        'error': error.message,
        'details': error.details
    }
    return jsonify(response), error.status_code

def handle_external_api_error(error: ExternalAPIError) -> tuple[Dict[str, Any], int]:
    """Handle errors from external API calls"""
    logger.error(f"External API error: {error.message}")
    response = {
        'error': get_translation('api_error', request.args.get('lang', 'vi')),
        'details': error.details
    }
    return jsonify(response), error.status_code

def handle_validation_error(error: ValidationError) -> tuple[Dict[str, Any], int]:
    """Handle input validation errors"""
    logger.warning(f"Validation error: {error.message}")
    response = {
        'error': error.message,
        'details': error.details
    }
    return jsonify(response), error.status_code

def handle_unexpected_error(error: Exception) -> tuple[Dict[str, Any], int]:
    """Handle unexpected errors"""
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    response = {
        'error': get_translation('unknown_error', request.args.get('lang', 'vi'))
    }
    return jsonify(response), 500

def with_error_handling(f: Callable) -> Callable:
    """Decorator to add error handling to route handlers"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.error(f"APIError: {e.message}", exc_info=True)
            return handle_api_error(e)
        except Exception as e:
            logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
            logger.error(format_exc())
            return handle_unexpected_error(e)
    return wrapper

def validate_image_file(image_file) -> None:
    """Validate uploaded image file"""
    if not image_file:
        raise ValidationError(get_translation('no_image'))
        
    if not image_file.filename:
        raise ValidationError(get_translation('invalid_image'))
        
    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in image_file.filename or \
       image_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        raise ValidationError(get_translation('invalid_image'))
        
    # Check file size (10MB max)
    if len(image_file.read()) > 10 * 1024 * 1024:
        raise ValidationError(get_translation('invalid_image'))
        
    # Reset file pointer
    image_file.seek(0)

def validate_language(lang: str) -> None:
    """Validate language parameter"""
    if lang not in {'vi', 'en'}:
        raise ValidationError("Invalid language parameter") 