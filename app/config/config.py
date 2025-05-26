import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    # Flask settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    
    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
    GOOGLE_SEARCH_CX = os.getenv('GOOGLE_SEARCH_CX')
    
    # Redis settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Cache settings
    CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))  # 1 hour
    CACHE_SIZE_LIMIT = int(os.getenv('CACHE_SIZE_LIMIT', 1000))
    
    # Rate limiting
    RATE_LIMIT = int(os.getenv('RATE_LIMIT', 5))  # requests
    RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', 60))  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Image processing
    MAX_IMAGE_SIZE = int(os.getenv('MAX_IMAGE_SIZE', 10 * 1024 * 1024))  # 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # API endpoints
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-latest:generateContent"
    GOOGLE_SEARCH_API_URL = 'https://www.googleapis.com/customsearch/v1'
    
    # Server Settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Cache Settings
    CACHE_TIMEOUT = 5  # seconds
    CACHE_SIZE_LIMIT = 1000
    
    # API Settings
    API_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_BACKOFF = 0.5
    
    # Image Processing
    IMAGE_QUALITY = 85  # JPEG quality
    
    # Production Numbers
    SPECIAL_PRODUCTION_NUMBERS: Dict[str, str] = {
        'ferrari sf90': '1,500 units per year',
        'ferrari 296': '1,200 units per year',
        'ferrari f8': '2,000 total units',
        'ferrari 488': '7,000 total units',
        'ferrari purosangue': '3,000 units per year',
        'ferrari roma': '2,000 units per year',
        'lamborghini revuelto': '10,112 in 2023',
        'lamborghini urus': '5,000 units per year'
    }
    
    # Popular Brands
    POPULAR_BRANDS = {
        'kia', 'toyota', 'hyundai', 'honda', 'mazda', 'ford', 'chevrolet', 
        'nissan', 'mitsubishi', 'suzuki', 'volkswagen', 'bmw', 'audi', 
        'mercedes', 'lexus', 'vinfast', 'peugeot', 'renault', 'fiat', 
        'skoda', 'seat', 'chery', 'geely', 'byd', 'great wall', 'dongfeng', 
        'baic', 'faw', 'gac'
    }
    
    # Technical Labels
    TECH_LABELS = {
        "Configuration": "Cấu hình",
        "Displacement": "Dung tích xy-lanh",
        "Turbo/Supercharging": "Tăng áp/Siêu nạp",
        "Transmission": "Hộp số",
        "Seating": "Ghế ngồi",
        "Dashboard": "Bảng điều khiển",
        "Technology": "Công nghệ",
        "Key Features": "Tính năng chính"
    }
    
    # Rarity Thresholds
    RARITY_THRESHOLDS = {
        'ultra_rare': 100,      # ★★★★★
        'very_rare': 500,       # ★★★★☆
        'rare': 1000,           # ★★★★☆
        'uncommon': 2000,       # ★★★☆☆
        'common': 5000,         # ★★☆☆☆
        'mass_produced': 10000  # ★☆☆☆☆
    }
    
    # Mass Production Numbers
    MASS_PRODUCTION_NUMBERS = {100000, 200000, 500000, 1000000, 10000000}

    # API Configuration
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-latest:generateContent"
    
    # Image Processing
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_COMPRESSED_SIZE = 800 * 1024  # 800KB
    
    # Logging
    LOG_LEVEL = "DEBUG"
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    
    # Server
    DEBUG = True 

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            'GEMINI_API_KEY',
            'GOOGLE_SEARCH_API_KEY',
            'GOOGLE_SEARCH_CX'
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
            
        return True 