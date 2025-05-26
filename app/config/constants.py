from typing import Dict, Set

# Cache settings
CACHE_TIMEOUT = 5  # seconds
CACHE_SIZE_LIMIT = 1000

# API Keys
GOOGLE_SEARCH_API_KEY = 'AIzaSyDSCmFmjPX1OdBQ3Ro4qSC3C6skEB0nI-o'
GOOGLE_SEARCH_CX = 'a3a26a1f03cc84ea4'

# Production numbers for special cars
SPECIAL_PRODUCTION_NUMBERS: Dict[str, str] = {
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

# Popular car brands
POPULAR_BRANDS: Set[str] = {
    'kia', 'toyota', 'hyundai', 'honda', 'mazda', 'ford', 'chevrolet', 'nissan', 'mitsubishi',
    'suzuki', 'volkswagen', 'bmw', 'audi', 'mercedes', 'lexus', 'vinfast', 'peugeot', 'renault',
    'fiat', 'skoda', 'seat', 'chery', 'geely', 'byd', 'great wall', 'dongfeng', 'baic', 'faw', 'gac'
}

# Technical labels for translation
TECH_LABELS: Dict[str, str] = {
    "Configuration": "Cấu hình",
    "Displacement": "Dung tích xy-lanh",
    "Turbo/Supercharging": "Tăng áp/Siêu nạp",
    "Transmission": "Hộp số",
    "Seating": "Ghế ngồi",
    "Dashboard": "Bảng điều khiển",
    "Technology": "Công nghệ",
    "Key Features": "Tính năng chính"
}

# Mass production numbers
MASS_PRODUCTION_NUMBERS: Set[int] = {100000, 200000, 500000, 1000000, 10000000}

# Rarity thresholds
RARITY_THRESHOLDS = {
    'very_rare': 100,
    'rare': 500,
    'limited': 1000,
    'semi_limited': 2000,
    'mass_produced': 5000
} 