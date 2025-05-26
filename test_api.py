import requests
import json
import time

def test_analyze_car():
    url = 'http://127.0.0.1:5000/analyze_car'
    
    # Open the test image file
    with open('test_car.jpg', 'rb') as image_file:
        files = {'image': ('test_car.jpg', image_file, 'image/jpeg')}
        data = {'lang': 'vi'}  # Test with Vietnamese language
        
        try:
            start = time.time()
            response = requests.post(url, files=files, data=data)
            elapsed = time.time() - start
            print(f"Status Code: {response.status_code}")
            print(f"Elapsed Time: {elapsed:.2f} seconds")
            
            if response.status_code == 200:
                result = response.json()
                print("\nResponse Data:")
                print(json.dumps(safe_print_result(result), indent=2, ensure_ascii=False))
                
                # Kiểm tra các trường quan trọng
                for lang in ['result_en', 'result_vi']:
                    print(f"\nChecking fields for {lang}:")
                    required_fields = [
                        'car_name', 'brand', 'year', 'price', 'power', 'acceleration', 'top_speed',
                        'description', 'engine_detail', 'interior', 'features', 'number_produced', 'rarity', 'logo_url'
                    ]
                    missing = []
                    res = result.get(lang, {})
                    for field in required_fields:
                        if field not in res or res[field] in [None, '', [], {}]:
                            missing.append(field)
                    if missing:
                        print(f"  Missing fields: {missing}")
                    else:
                        print("  All required fields present.")
            else:
                print("Error:", response.text)
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")

def safe_print_result(result, max_length=100):
    if isinstance(result, dict):
        result_copy = {}
        for k, v in result.items():
            if isinstance(v, (dict, list)):
                result_copy[k] = safe_print_result(v, max_length)
            elif isinstance(v, str) and (len(v) > max_length or 'base64' in k or v.startswith('data:image')):
                result_copy[k] = '[omitted]'
            else:
                result_copy[k] = v
        return result_copy
    elif isinstance(result, list):
        return [safe_print_result(item, max_length) for item in result]
    else:
        return result

if __name__ == '__main__':
    test_analyze_car() 