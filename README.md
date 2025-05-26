# Car AI Backend

Backend API cho ứng dụng phân tích xe hơi sử dụng AI, được xây dựng với Flask và Google Gemini API.

## Tính năng

- Phân tích hình ảnh xe hơi
- Nhận diện logo và thương hiệu
- Trích xuất thông tin chi tiết về xe
- Hỗ trợ đa ngôn ngữ (Tiếng Việt/Anh)
- Cache và rate limiting
- Xử lý lỗi toàn diện

## Yêu cầu hệ thống

- Python 3.8+
- OpenCV
- Flask
- Google Generative AI
- Các thư viện khác (xem requirements.txt)

## Cài đặt

1. Clone repository:
```bash
git clone <repository_url>
cd car-ai-backend
```

2. Tạo môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Tạo file .env:
```bash
cp .env.example .env
```
Sau đó cập nhật các biến môi trường trong file .env với API keys của bạn.

## Chạy ứng dụng

1. Chạy trong môi trường development:
```bash
python app.py
```

2. Chạy với Gunicorn (production):
```bash
gunicorn app:app
```

## API Endpoints

### POST /analyze_car
Phân tích hình ảnh xe hơi

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - image: File hình ảnh
  - lang: Ngôn ngữ (vi/en)

**Response:**
```json
{
    "car_name": "string",
    "brand": "string",
    "year": "string",
    "price": "string",
    "power": "string",
    "acceleration": "string",
    "top_speed": "string",
    "number_produced": "string",
    "rarity": "string",
    "engine_detail": "string",
    "interior": "string",
    "features": ["string"],
    "description": "string"
}
```

### POST /translate_history
Dịch lịch sử phân tích

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
  - record: Object chứa thông tin cần dịch
  - lang: Ngôn ngữ đích (vi/en)

### GET /test_api
Kiểm tra kết nối API

## Cấu trúc thư mục

```
car-ai-backend/
├── app/
│   ├── config/
│   │   ├── config.py
│   │   ├── constants.py
│   │   └── translations.py
│   ├── services/
│   │   ├── car_analyzer.py
│   │   ├── gemini_service.py
│   │   └── image_processor.py
│   └── utils/
│       ├── cache_manager.py
│       └── error_handler.py
├── app.py
├── requirements.txt
└── .env
```

## Xử lý lỗi

Ứng dụng sử dụng hệ thống xử lý lỗi toàn diện với các loại lỗi:
- ImageProcessingError
- ExternalAPIError
- ValidationError

Mỗi lỗi sẽ trả về response JSON với:
- Mã lỗi HTTP phù hợp
- Thông báo lỗi
- Chi tiết lỗi (nếu có)

## Cache và Rate Limiting

- Cache timeout: 5 giây
- Giới hạn kích thước cache: 1000 entries
- Rate limiting: 1 request/5 giây cho mỗi client

## Đóng góp

Mọi đóng góp đều được hoan nghênh. Vui lòng tạo issue hoặc pull request.

## License

MIT License