import re
import os
import requests
from datetime import datetime
from collections import OrderedDict
import math
import io
from PIL import Image
import logging
import base64

# Configure logging
logger = logging.getLogger(__name__)

# Special production numbers for rare/limited cars
SPECIAL_PRODUCTION_NUMBERS = {
    'lamborghini veneno': '14 (5 coupe + 9 roadster)',
    'lamborghini veneno roadster': '14 (5 coupe + 9 roadster)',
    'lamborghini revuelto': '10,112 in 2023',
    'lamborghini centenario': '40',
    'lamborghini reventon': '21',
    'lamborghini sesto elemento': '20',
    'lamborghini egoista': '1',
    'ferrari laferrari': '500',
    'ferrari fxx k': '40',
    'ferrari monza sp1': '499',
    'ferrari monza sp2': '499',
    'ferrari f8 tributo': '2,000 total units',
    'ferrari sf90 stradale': '799 coupe + 599 spider',
    'ferrari 296 gtb': '1,200 units per year',
    'ferrari 488 gtb': '7,000 total units',
    'ferrari purosangue': '3,000 units per year',
    'ferrari roma': '2,000 units per year',
    'ferrari 812 competizione': '999 units',
    'ferrari daytona sp3': '599 units',
    'bugatti chiron super sport 300+': '30',
    'bugatti la voiture noire': '1',
    'bugatti centodieci': '10',
    'koenigsegg jesko absolut': '125',
    'koenigsegg ccxr trevita': '3',
    'koenigsegg one:1': '7',
    'pagani zonda cinque': '5',
    'pagani huayra bc': '20',
    'mclaren f1': '106',
    'mclaren speedtail': '106',
    'mclaren senna': '500',
    'aston martin valkyrie': '150',
    'aston martin one-77': '77',
    'porsche 918 spyder': '918',
    'porsche carrera gt': '1,270',
    'rimac nevera': '150',
    'hennessey venom f5': '24',
    'byd seal': 'khoảng 30,000 xe mỗi năm (ước tính 2023, theo CarNewsChina)',
    'xiaomi su7': 'khoảng 20,000 xe năm 2024 (ước tính)',
}

# Add logo cache at the top of the file
_logo_cache = {}

def download_and_encode_logo(url):
    """Download logo and encode to base64"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=10, verify=True)
        if response.status_code != 200:
            logger.warning(f"Failed to download logo from {url}, status: {response.status_code}")
            return None
            
        content_type = response.headers.get('content-type', '').lower()
        # Only accept PNG/JPG
        if 'image/png' in content_type or 'image/jpeg' in content_type or 'image/jpg' in content_type:
            img_data = base64.b64encode(response.content).decode('utf-8')
            prefix = 'png' if 'png' in content_type else 'jpeg'
            return f'data:image/{prefix};base64,{img_data}'
        # Skip SVG/WebP
        logger.warning(f"Logo content type {content_type} is not PNG/JPG, skipping.")
        return None
        
    except Exception as e:
        logger.error(f"Error downloading logo from {url}: {str(e)}")
        return None

def validate_logo_url(url):
    """Validate if logo URL is accessible and returns valid image data"""
    if not url:
        return False
        
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
        
        # Try to download image directly
        response = requests.get(url, headers=headers, timeout=10, verify=True)
        if response.status_code != 200:
            logger.warning(f"Failed to download logo from {url}, status: {response.status_code}")
            return False
            
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if not any(t in content_type for t in ['image/jpeg', 'image/png', 'image/gif', 'image/svg+xml']):
            logger.warning(f"Invalid content type {content_type} for {url}")
            return False
            
        # Verify image data
        try:
            img = Image.open(io.BytesIO(response.content))
            
            # Check image size
            width, height = img.size
            if width < 50 or height < 50:  # Skip very small images
                logger.warning(f"Image too small: {width}x{height} for {url}")
                return False
            if width > 5000 or height > 5000:  # Skip very large images
                logger.warning(f"Image too large: {width}x{height} for {url}")
                return False
                
            # Try to load image data
            img.load()
            
            # Additional format check
            if img.format not in ['JPEG', 'PNG', 'GIF', 'SVG']:
                logger.warning(f"Unsupported image format: {img.format} for {url}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing image data for {url}: {str(e)}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for {url}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error validating {url}: {str(e)}")
        return False

def search_logo_url(brand):
    """Search for car brand logo using Google Custom Search API, only return PNG/JPG base64 data URLs"""
    if not brand:
        return None
    brand_lower = brand.lower().strip()
    queries = [
        f"{brand} logo",
        f"{brand} car logo",
        f"{brand} automotive logo",
        f"{brand} official logo",
        f"{brand} brand logo",
        f"{brand} company logo",
        f"{brand} logo transparent",
        f"{brand} logo vector"
    ]
    for query in queries:
        try:
            url = (
                f"https://www.googleapis.com/customsearch/v1"
                f"?key={os.getenv('GOOGLE_SEARCH_API_KEY')}"
                f"&cx={os.getenv('GOOGLE_SEARCH_CX')}"
                f"&searchType=image"
                f"&num=10"
                f"&q={query}"
                f"&safe=active"
            )
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json()
            if 'items' in data and len(data['items']) > 0:
                for item in data['items']:
                    link = item.get('link', '')
                    if not link:
                        continue
                    encoded_logo = download_and_encode_logo(link)
                    if encoded_logo:
                        logger.info(f"Found valid PNG/JPG logo and encoded: {link}")
                        return encoded_logo
        except Exception as e:
            logger.error(f"Error searching logo for query '{query}': {e}")
            continue
    return None

def get_default_logo(brand):
    """Get logo URL for a brand using Google Search API with caching and fallback"""
    if not brand:
        return None
        
    brand_key = brand.strip().lower()
    
    # Check cache first
    if brand_key in _logo_cache:
        cached_logo = _logo_cache[brand_key]
        if cached_logo.startswith('data:image'):
            return cached_logo
        # If cached URL is not base64, try to download it
        encoded_logo = download_and_encode_logo(cached_logo)
        if encoded_logo:
            _logo_cache[brand_key] = encoded_logo
            return encoded_logo
        else:
            # If cached URL is not accessible, remove from cache
            del _logo_cache[brand_key]
    
    try:
        # Try to get logo URL
        logo_url = search_logo_url(brand_key)
        if logo_url:
            # Cache the result
            _logo_cache[brand_key] = logo_url
            return logo_url
            
        # If no logo found, try with common brand name variations
        brand_variations = {
            'mercedes': 'mercedes-benz',
            'bmw': 'bmw',
            'audi': 'audi',
            'toyota': 'toyota',
            'honda': 'honda',
            'nissan': 'nissan',
            'ford': 'ford',
            'chevrolet': 'chevrolet',
            'hyundai': 'hyundai',
            'kia': 'kia',
            'volkswagen': 'volkswagen',
            'volvo': 'volvo',
            'lexus': 'lexus',
            'infiniti': 'infiniti',
            'acura': 'acura',
            'lincoln': 'lincoln',
            'cadillac': 'cadillac',
            'buick': 'buick',
            'gmc': 'gmc',
            'chrysler': 'chrysler',
            'dodge': 'dodge',
            'jeep': 'jeep',
            'ram': 'ram',
            'mitsubishi': 'mitsubishi',
            'subaru': 'subaru',
            'mazda': 'mazda',
            'suzuki': 'suzuki',
            'isuzu': 'isuzu',
            'mini': 'mini',
            'smart': 'smart',
            'fiat': 'fiat',
            'alfa romeo': 'alfa romeo',
            'maserati': 'maserati',
            'ferrari': 'ferrari',
            'lamborghini': 'lamborghini',
            'porsche': 'porsche',
            'bentley': 'bentley',
            'rolls royce': 'rolls-royce',
            'aston martin': 'aston-martin',
            'jaguar': 'jaguar',
            'land rover': 'land-rover',
            'range rover': 'range-rover',
            'lotus': 'lotus',
            'mclaren': 'mclaren',
            'bugatti': 'bugatti',
            'koenigsegg': 'koenigsegg',
            'pagani': 'pagani',
            'rimac': 'rimac',
            'byd': 'byd',
            'nio': 'nio',
            'xpeng': 'xpeng',
            'li auto': 'li-auto',
            'lynk & co': 'lynk-co',
            'geely': 'geely',
            'haval': 'haval',
            'great wall': 'great-wall',
            'chery': 'chery',
            'jac': 'jac',
            'soueast': 'soueast',
            'dongfeng': 'dongfeng',
            'faw': 'faw',
            'baic': 'baic',
            'changan': 'changan',
            'gac': 'gac',
            'saic': 'saic',
            'roewe': 'roewe',
            'mg': 'mg',
            'maxus': 'maxus'
        }
        
        # Try with brand variations
        for variation in brand_variations:
            if variation in brand_key:
                logo_url = search_logo_url(brand_variations[variation])
                if logo_url:
                    _logo_cache[brand_key] = logo_url
                    return logo_url
                    
    except Exception as e:
        logger.error(f"Error in get_default_logo: {e}")
        
    return None

def normalize_car_name(name):
    """Normalize car name by removing duplicates and standardizing format"""
    if not name:
        return ''
    parts = name.split()
    normalized = []
    for part in parts:
        if not normalized or part.lower() != normalized[-1].lower():
            normalized.append(part)
    return ' '.join(normalized)

def clean_brand_name(brand):
    """Clean brand name by removing special characters and duplicates"""
    if not brand:
        return ''
    brand = re.sub(r'[^a-zA-Z0-9 ]', '', brand)
    brand = brand.strip()
    parts = brand.split()
    if parts:
        seen = set()
        cleaned = []
        for part in parts:
            if part.lower() not in seen:
                cleaned.append(part)
                seen.add(part.lower())
        return ' '.join(cleaned)
    return brand

def fix_number_produced(name, desc, fallback, lang='en'):
    """Fix production number based on car name and description"""
    name_key = (name or '').lower().strip()
    
    # Check special production numbers first
    if name_key in SPECIAL_PRODUCTION_NUMBERS:
        return SPECIAL_PRODUCTION_NUMBERS[name_key]
        
    fallback_str = str(fallback).lower() if fallback is not None else ''
    
    # Handle special cases
    if 'urus' in name_key:
        return '20,000 units (est. as of 2023)' if lang == 'en' else 'khoảng 20.000 xe (ước tính 2023)'
    if 'revuelto' in name_key:
        return '10,112 in 2023' if lang == 'en' else '10.112 xe năm 2023'
    if 'sián' in name_key:
        return '63 coupe + 19 roadster' if lang == 'en' else '63 coupe + 19 roadster'
    if 'sf90' in name_key:
        return '799 coupe + 599 spider' if lang == 'en' else '799 coupe + 599 spider'
        
    # Handle invalid or missing numbers
    if (not fallback or any(x in fallback_str for x in ['n/a', 'unknown', 'not found', 'year', 'present', 'hiện tại', 'no', 'none', '', '0']) or 
        re.fullmatch(r'\d{4}(-\d{4}|-present|)', fallback_str)):
        return 'Over 1,000 units' if lang == 'en' else 'Trên 1.000 xe'
        
    # Handle small numbers
    match = re.search(r'\d{1,3}(?:,\d{3})*|\d+', fallback_str)
    if match:
        num = int(match.group(0).replace(',', ''))
        if num < 1000:
            return 'Over 1,000 units' if lang == 'en' else 'Trên 1.000 xe'
            
    return fallback

def convert_number_produced(number_produced, lang):
    """Convert production number format based on language"""
    if not number_produced:
        return ''
    if lang == 'vi':
        s = number_produced.replace('units/year', 'xe/năm').replace('units', 'xe')
        s = s.replace('per year', 'xe/năm').replace('unit', 'xe')
        return s
    return number_produced

def average_year(year_str):
    """Tính trung bình cộng của khoảng năm, làm tròn. Nếu có 'Present' thì lấy năm đầu tiên."""
    if not year_str:
        return year_str
    if '-' in year_str:
        parts = year_str.replace(' ', '').split('-')
        try:
            years = [int(p) for p in parts if p.isdigit()]
            if years:
                return str(years[0])
        except Exception:
            pass
    return year_str

def average_price(price_str):
    """Tính trung bình cộng của khoảng giá, trả về dạng $xx,xxx."""
    if not price_str:
        return price_str
    import re
    # Loại bỏ ký tự $ và khoảng trắng
    cleaned = price_str.replace('$', '').replace('USD', '').replace('usd', '').replace('–', '-').replace('—', '-').strip()
    # Tìm tất cả số trong chuỗi
    nums = re.findall(r'[\d,]+', cleaned)
    nums = [int(n.replace(',', '')) for n in nums if n]
    if len(nums) >= 2:
        avg = int(sum(nums) / len(nums))
        return f"${avg:,}"
    elif len(nums) == 1:
        return f"${nums[0]:,}"
    return price_str 