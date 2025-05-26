"""
Translation strings for the application
"""

from typing import Dict, Any

def get_translation(key: str, lang: str = 'vi', category: str = 'messages') -> str:
    """
    Get translation for a given key and language
    
    Args:
        key: Translation key
        lang: Language code ('vi' or 'en')
        category: Translation category ('messages' or 'labels')
        
    Returns:
        str: Translated text
    """
    translations = {
        'messages': {
            'vi': {
                'no_image': 'Vui lòng tải lên một hình ảnh',
                'invalid_image': 'Hình ảnh không hợp lệ',
                'processing_error': 'Lỗi xử lý hình ảnh',
                'analysis_error': 'Lỗi phân tích hình ảnh',
                'translation_error': 'Lỗi dịch văn bản',
                'api_error': 'Lỗi kết nối API',
                'rate_limit': 'Vui lòng đợi một chút trước khi thử lại',
                'unknown_error': 'Đã xảy ra lỗi không mong muốn'
            },
            'en': {
                'no_image': 'Please upload an image',
                'invalid_image': 'Invalid image',
                'processing_error': 'Error processing image',
                'analysis_error': 'Error analyzing image',
                'translation_error': 'Error translating text',
                'api_error': 'API connection error',
                'rate_limit': 'Please wait a moment before trying again',
                'unknown_error': 'An unexpected error occurred'
            }
        },
        'labels': {
            'vi': {
                'car_name': 'Tên xe',
                'brand': 'Hãng xe',
                'year': 'Năm sản xuất',
                'price': 'Giá',
                'power': 'Công suất',
                'acceleration': 'Tăng tốc 0-100 km/h',
                'top_speed': 'Vận tốc tối đa',
                'engine_details': 'Chi tiết động cơ',
                'interior_details': 'Chi tiết nội thất',
                'features_list': 'Tính năng',
                'description': 'Mô tả',
                'processing_time': 'Thời gian xử lý',
                'analysis_result': 'Kết quả phân tích'
            },
            'en': {
                'car_name': 'Car Name',
                'brand': 'Brand',
                'year': 'Year',
                'price': 'Price',
                'power': 'Power',
                'acceleration': '0-60 mph',
                'top_speed': 'Top Speed',
                'engine_details': 'Engine Details',
                'interior_details': 'Interior Details',
                'features_list': 'Features',
                'description': 'Description',
                'processing_time': 'Processing Time',
                'analysis_result': 'Analysis Result'
            }
        }
    }
    
    try:
        return translations[category][lang][key]
    except KeyError:
        return key 