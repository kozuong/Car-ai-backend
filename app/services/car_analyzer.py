import logging
from datetime import datetime
from .gemini_service import GeminiService
import requests
import re
from typing import Dict, Any, Optional, Tuple
from app.config.constants import (
    SPECIAL_PRODUCTION_NUMBERS,
    POPULAR_BRANDS,
    TECH_LABELS,
    MASS_PRODUCTION_NUMBERS,
    RARITY_THRESHOLDS
)
from app.utils.error_handler import APIError
from app.services.google_custom_search_service import GoogleCustomSearchService
import base64

logger = logging.getLogger(__name__)

class CarAnalyzer:
    def __init__(self):
        self.gemini_service = GeminiService()
        self.google_search_service = GoogleCustomSearchService()
        self.revuelto_features = [
            'y-shaped headlights', 'y shaped headlights', 'đèn hình chữ y',
            'hexagonal exhaust', 'hexagonal tailpipes', 'ống xả lục giác',
            'large air intakes', 'nhiều khe gió lớn',
            'v12 hybrid', 'v12', '2023', 'lamborghini logo', 'revuelto'
        ]
        
        self.sf90_features = [
            '4 round taillights', '4 đèn hậu tròn', 'center exhaust', 'exhaust center',
            'hybrid v8', '830hp', '830 hp', '2020', 'ferrari logo', 'sf90', 'stradale',
            'hybrid', 'plug-in hybrid', '4 đèn tròn', '4 đèn hậu', '4 đèn led', '4 led',
        ]

    def normalize_car_name(self, name: str) -> str:
        """Normalize car name by removing duplicate words"""
        if not name:
            return ''
        parts = name.split()
        normalized = []
        for part in parts:
            if not normalized or part.lower() != normalized[-1].lower():
                normalized.append(part)
        return ' '.join(normalized)

    def clean_brand_name(self, brand: str) -> str:
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

    def simplify_number_produced(self, text: str, lang: str = 'vi') -> str:
        """Simplify production number text"""
        if not text:
            return ''
        match = re.search(r'\d{1,3}(?:,\d{3})*|\d+', text)
        if match:
            number = match.group(0).replace(',', '')
            if re.search(r'(per year|mỗi năm|/year|năm)', text, re.IGNORECASE):
                return f'{number} {"xe/năm" if lang == "vi" else "units/year"}'
            return f'{number} {"xe" if lang == "vi" else "units"}'
        return text

    def calculate_rarity(self, number_produced: str) -> str:
        """Tính rarity với mức .5 sao"""
        try:
            match = re.search(r'\d+', number_produced.replace(",", ""))
            if match:
                num = int(match.group(0))
                # Bảng phân loại mới
                if num <= 50:
                    return "★★★★★"
                elif num <= 500:
                    return "★★★★½"
                elif num <= 2000:
                    return "★★★½☆"
                elif num <= 10000:
                    return "★★★☆☆"
                elif num <= 100000:
                    return "★★☆☆☆"
                else:
                    return "★☆☆☆☆"
            return "★☆☆☆☆"
        except Exception:
            return "★☆☆☆☆"

    def is_revuelto(self, description: str, car_name: str) -> bool:
        """Check if car is likely a Lamborghini Revuelto"""
        desc = (description or '').lower() + ' ' + (car_name or '').lower()
        return any(f in desc for f in self.revuelto_features) and 'lamborghini' in desc

    def is_sf90(self, description: str, car_name: str) -> bool:
        """Check if car is likely a Ferrari SF90"""
        desc = (description or '').lower() + ' ' + (car_name or '').lower()
        return any(f in desc for f in self.sf90_features) and 'ferrari' in desc

    def is_popular_brand(self, brand_name: str) -> bool:
        """Check if brand is a popular mass-market brand"""
        return any(b in (brand_name or '').lower() for b in POPULAR_BRANDS)

    def extract_number(self, num_str: str) -> Optional[int]:
        """Extract first number from string"""
        match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)', str(num_str))
        if match:
            return int(match.group(0).replace(',', ''))
        return None

    def get_production_number(self, car_name: str, description: str) -> str:
        """Get production number for car"""
        car_name_key = car_name.lower().strip() if car_name else ''
        
        # Check special production numbers first
        if car_name_key in SPECIAL_PRODUCTION_NUMBERS:
            return SPECIAL_PRODUCTION_NUMBERS[car_name_key]
        
        # Check for Urus
        if 'urus' in car_name_key:
            return '5,000 units per year'
        
        # Check for popular brands
        if self.is_popular_brand(car_name_key):
            return 'Hơn 10,000 xe mỗi năm'
        
        # Default based on car type
        if 'ferrari' in car_name_key:
            if 'sf90' in car_name_key:
                return '1,500 units per year'
            elif '296' in car_name_key:
                return '1,200 units per year'
            elif 'f8' in car_name_key:
                return '2,000 total units'
            elif '488' in car_name_key:
                return '7,000 total units'
            elif 'purosangue' in car_name_key:
                return '3,000 units per year'
            elif 'roma' in car_name_key:
                return '2,000 units per year'
            else:
                return 'Ước tính dưới 5,000 xe mỗi năm dựa trên các mẫu Ferrari cùng phân khúc.'
        elif 'lamborghini' in car_name_key:
            if 'revuelto' in car_name_key:
                return '10,112 in 2023'
            else:
                return 'Ước tính dưới 1,000 xe mỗi năm dựa trên các mẫu Lamborghini cùng phân khúc.'
        elif 'suv' in car_name_key or 'urus' in car_name_key:
            return '5,000 units per year'
        elif 'supercar' in description.lower() or 'hypercar' in description.lower():
            return 'Ước tính dưới 1,000 xe trên toàn thế giới.'
        else:
            return 'Ước tính dưới 10,000 xe mỗi năm dựa trên các mẫu xe cùng loại.'

    def replace_tech_labels(self, text: str) -> str:
        """Replace technical labels with translated versions"""
        for en, vi in TECH_LABELS.items():
            text = re.sub(rf'(?im)^\s*{en}\s*:?\s*', vi + ': ', text)
        return text

    def ensure_complete_data(self, data: Dict[str, Any], car_name: str, lang: str) -> Dict[str, Any]:
        """Ensure all required fields are present and valid"""
        if not data.get('description') or 'detailed information' in data['description'].lower():
            brand = data.get('brand', '')
            if lang == 'vi':
                data['description'] = f'{car_name} là một mẫu xe của {brand}. Hiện chưa có mô tả chi tiết.'
            else:
                data['description'] = f'{car_name} is a model from {brand}. No detailed description available.'

        if data.get('price'):
            price = data['price'].strip()
            if '$' not in price:
                data['price'] = f"{price} $"

        return data

    def ensure_language_consistency(self, data: Dict[str, Any], lang: str) -> Dict[str, Any]:
        """Ensure all text is in the correct language"""
        if lang == 'vi':
            for field in ['description', 'engine_detail', 'interior']:
                if field in data and data[field]:
                    data[field] = self.replace_tech_labels(data[field])
        return data

    def extract_fields(self, text, yolo_brand=None):
        """Extract car information from text."""
        try:
            logger.info(f"[extract_fields] Raw text input: {repr(text)[:500]}")
            fields = {
                "brand": "", "model": "", "year": "",
                "price": "", "power": "", "acceleration": "",
                "top_speed": "", "number_produced": "", "rarity": "",
                "description": {
                    "overview": [],
                    "engine": [],
                    "interior": [],
                    "features": []
                }
            }
            current_field = None
            current_section = None
            features = []
            lines = text.strip().splitlines()
            in_description = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Check for main field headers and section headers
                if line.endswith(':'):
                    header = line[:-1].lower()
                    if header == "description":
                        in_description = True
                        current_field = "description"
                    elif header == "performance":
                        in_description = False
                        current_field = "performance"
                    elif in_description:
                        if "overview" in header:
                            current_section = "overview"
                        elif "engine" in header:
                            current_section = "engine"
                        elif "interior" in header:
                            current_section = "interior"
                        elif "features" in header:
                            current_section = "features"
                    continue
                # Handle performance metrics
                if current_field == "performance":
                    try:
                        if "power:" in line.lower():
                            fields["power"] = line.split(":", 1)[1].strip()
                        elif "0-60" in line.lower() or "0-100" in line.lower():
                            fields["acceleration"] = line.split(":", 1)[1].strip()
                        elif "top speed" in line.lower():
                            fields["top_speed"] = line.split(":", 1)[1].strip()
                    except Exception as e:
                        logger.error(f"[extract_fields] Error parsing performance line: '{line}' ({e})")
                    continue
                # Handle other fields
                if ":" in line and not line.startswith('-'):
                    try:
                        key, value = line.split(":", 1)
                        key = key.strip().lower()
                        value = value.strip()
                        if "brand" in key:
                            fields["brand"] = value
                        elif "model" in key:
                            fields["model"] = value
                        elif "year" in key:
                            fields["year"] = value
                        elif "price" in key:
                            fields["price"] = value
                        elif "number produced" in key:
                            fields["number_produced"] = value
                        elif "rarity" in key:
                            fields["rarity"] = value
                    except Exception as e:
                        logger.error(f"[extract_fields] Error parsing line: '{line}' ({e})")
                        continue
                elif in_description:
                    # Handle description sections
                    if current_section == "overview" and not line.startswith('-'):
                        fields["description"]["overview"].append(line)
                    elif line.startswith('-'):
                        if current_section == "engine":
                            fields["description"]["engine"].append(line.strip('- '))
                        elif current_section == "interior":
                            fields["description"]["interior"].append(line.strip('- '))
                        elif current_section == "features":
                            features.append(line.strip('- '))
            # Construct formatted description
            description_parts = []
            engine_detail = ""
            interior = ""
            if fields["description"]["overview"]:
                overview = " ".join(fields["description"]["overview"]).strip()
                if overview:
                    description_parts.append(overview)
            if fields["description"]["engine"]:
                engine_detail = "\n".join(fields["description"]["engine"])
            if fields["description"]["interior"]:
                interior = "\n".join(fields["description"]["interior"])
            final_description = "\n".join(description_parts)
            car_name = f"{fields['brand']} {fields['model']}".strip()
            if not final_description or len(final_description.split()) < 8 or 'no detailed description' in final_description.lower():
                logger.error(f"[extract_fields] Description thiếu chi tiết hoặc không hợp lệ: {final_description}")
                raise ValueError("Description is missing or not detailed enough. Please retry with a more detailed prompt.")
            if not car_name or car_name.lower() in ["", "unknown", "unknown car"]:
                logger.warning(f"[extract_fields] Không nhận diện được brand/model từ text: {repr(text)[:200]}")
                car_name = ""
                fields['brand'] = ""
                fields['model'] = ""
                fields['year'] = ""
                fields['price'] = ""
                fields['power'] = ""
                fields['acceleration'] = ""
                fields['top_speed'] = ""
                fields['number_produced'] = ""
                fields['rarity'] = ""
                fields['description']['overview'] = []
            SPECIAL_CARS = {"lamborghini veneno": 14, "ferrari laferrari": 499, "mclaren p1": 375, "porsche 918 spyder": 918}
            car_name_key = car_name.lower().strip()
            if car_name_key in SPECIAL_CARS:
                fields["number_produced"] = f"{SPECIAL_CARS[car_name_key]} units"
            else:
                nums = [int(x.replace(",", "")) for x in re.findall(r"\d+", fields["number_produced"]) if not (len(x) == 4 and int(x) > 1900)]
                if nums:
                    small_nums = [n for n in nums if n < 100]
                    if small_nums:
                        fields["number_produced"] = f"{min(small_nums)} units"
                    else:
                        fields["number_produced"] = f"{max(nums)} units"
                else:
                    fields["number_produced"] = "Unknown"
            if not fields["number_produced"] or fields["number_produced"].strip() == '':
                fields["number_produced"] = "Over 1,000 units"
            if not fields["rarity"] or fields["rarity"].strip() == '':
                fields["rarity"] = "-"
            try:
                fields["price"] = self.format_price(fields["price"])
            except Exception as e:
                logger.error(f"[extract_fields] Error formatting price: {fields['price']} ({e})")
                fields["price"] = "N/A"
            logger.info(f"[extract_fields] Parsed fields: car_name={car_name}, year={fields['year']}, price={fields['price']}, power={fields['power']}, acceleration={fields['acceleration']}, top_speed={fields['top_speed']}, number_produced={fields['number_produced']}, rarity={fields['rarity']}")
            return (
                car_name, 
                fields["year"] or "N/A", 
                fields["price"] or "N/A",
                fields["power"] or "N/A", 
                fields["acceleration"] or "N/A", 
                fields["top_speed"] or "N/A",
                fields["number_produced"] or "-",
                fields["rarity"] or "-",
                engine_detail or "No engine details available.",
                interior or "No interior details available.",
                features,
                final_description or "No detailed description available."
            )
        except Exception as e:
            logger.error(f"[extract_fields] Error in extract_fields: {str(e)} | text: {repr(text)[:300]}")
            return (
                "", "", "", "", "", "",
                "", "",
                "", "", [],
                ""
            )

    def google_search_number_produced(self, car_name):
        # Sử dụng Google Custom Search API để tìm số lượng sản xuất
        try:
            api_key = 'AIzaSyCaX7K-W_PZTuqjWsrl2AuVOiz732rix0E'
            cx = 'a3a26a1f03cc84ea4'
            query = f"{car_name} number produced OR production numbers OR production quantity"
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}"
            resp = requests.get(url)
            data = resp.json()
            if 'items' in data:
                for item in data['items']:
                    snippet = item.get('snippet', '')
                    # Tìm số trong snippet
                    match = re.search(r'(\d{1,3}(,\d{3})+|\d+)', snippet.replace(',', ''))
                    if match:
                        num = match.group(0).replace(',', '')
                        if num.isdigit():
                            return int(num)
            return None
        except Exception as e:
            return None

    def format_price(self, price_str):
        # Rút gọn giá dạng '4,000,000 - 5,000,000' thành '~ 4,500,000'
        if not price_str:
            return price_str
        # Loại bỏ ký tự $ và USD
        price_str = price_str.replace('$', '').replace('USD', '').replace('usd', '').strip()
        # Tìm các số
        nums = re.findall(r'[\d,]+', price_str)
        nums = [int(n.replace(',', '')) for n in nums if n]
        if len(nums) == 2:
            avg = int((nums[0] + nums[1]) / 2)
            return f'$ {avg:,}'.replace(',', ' ')
        elif len(nums) == 1:
            return f'$ {nums[0]:,}'.replace(',', ' ')
        # Nếu không có số, trả về nguyên bản
        return f'$ {price_str}' if price_str else price_str 

    def get_price_and_number_produced(self, car_name: str) -> dict:
        """
        Sử dụng Google Custom Search API để lấy giá và số lượng sản xuất, trả về giá trung bình nếu có nhiều kết quả
        """
        try:
            price_results = self.google_search_service.search_price(car_name)
            number_results = self.google_search_service.search_number_produced(car_name)
            
            # Lấy logo URL và chuyển đổi thành base64
            logo_url = self.google_search_service.search_logo(car_name)
            if logo_url:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Referer': 'https://www.google.com/'
                    }
                    response = requests.get(logo_url, headers=headers, timeout=10, verify=True)
                    if response.status_code == 200:
                        # Chuyển đổi sang base64
                        img_data = base64.b64encode(response.content).decode('utf-8')
                        logo_url = f"data:image/png;base64,{img_data}"
                except Exception as e:
                    logger.error(f"Error converting logo to base64: {str(e)}")
                    logo_url = None
            
            # Ưu tiên số lượng sản xuất từ Google Search nếu có số
            number_produced = self._average_number(number_results)
            price = self._average_price(price_results)
            
            return {
                'price': price,
                'number_produced': number_produced,
                'logo_url': logo_url
            }
        except Exception as e:
            logger.error(f"Error in get_price_and_number_produced: {str(e)}")
            return {
                'price': None,
                'number_produced': None,
                'logo_url': None
            }

    def _average_price(self, price_list):
        # Tính giá trung bình từ list giá
        if not price_list:
            return None
        nums = []
        for p in price_list:
            try:
                nums.extend([int(x.replace(",", "")) for x in re.findall(r"[\d,]+", p)])
            except:
                continue
        if not nums:
            return None
        return f'$ {int(sum(nums)/len(nums)):,}'.replace(",", " ")

    def _average_number(self, number_list):
        # Tính tổng số lượng từ list, cộng tất cả số trong chuỗi, bỏ qua năm
        if not number_list:
            return None
        total = 0
        for n in number_list:
            # Lấy tất cả số, bỏ qua năm (năm thường là 4 chữ số lớn hơn 1900)
            nums = [int(x.replace(",", "")) for x in re.findall(r"\d+", n) if not (len(x) == 4 and int(x) > 1900)]
            total += sum(nums)
        if total == 0:
            return None
        return f'{total:,}'

    def get_best_number_produced(self, car_name: str, gemini_number: str = None) -> str:
        """Lấy số lượng sản xuất tốt nhất từ Google Search, fallback Gemini, nếu không có trả về 'Unknown'"""
        google_snippets = self.google_search_service.search_number_produced(car_name)
        max_number = 0
        best_text = None
        for snippet in google_snippets:
            # Tìm tất cả số trong snippet
            numbers = [int(x.replace(',', '')) for x in re.findall(r'(\d{1,3}(?:,\d{3})+|\d+)', snippet) if int(x.replace(',', '')) > 0]
            for num in numbers:
                if num > max_number:
                    max_number = num
                    best_text = f"{num:,} units".replace(",", " ")
        # Nếu có số lớn hơn 10,000 thì dùng số đó
        if max_number >= 10000:
            return best_text
        # Nếu không có số hợp lý, fallback Gemini
        if gemini_number and any(c.isdigit() for c in gemini_number) and ('1,000' not in gemini_number and 'Over 1,000' not in gemini_number):
            return gemini_number
        # Nếu vẫn không có, trả về Unknown
        return "Unknown" 