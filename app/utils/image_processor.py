import cv2
import numpy as np
from PIL import Image
import io
import base64
import logging
from ..config.config import Config
from ultralytics import YOLO
import torch

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        # Load YOLO model for logo detection
        try:
            self.logo_model = YOLO('yolov8n.pt')  # Using YOLOv8 nano for speed
            logger.info("Successfully loaded YOLO model")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.logo_model = None

        # Define car brand logos to detect
        self.car_brands = {
            'lamborghini': ['bull', 'lamborghini'],
            'ferrari': ['horse', 'ferrari'],
            'porsche': ['porsche'],
            'mclaren': ['mclaren'],
            'bugatti': ['bugatti'],
            'koenigsegg': ['koenigsegg'],
            'pagani': ['pagani'],
            'aston martin': ['aston martin'],
            'bentley': ['bentley'],
            'rolls royce': ['rolls royce'],
            'mercedes': ['mercedes', 'benz'],
            'bmw': ['bmw'],
            'audi': ['audi'],
            'lexus': ['lexus'],
            'toyota': ['toyota'],
            'honda': ['honda'],
            'nissan': ['nissan'],
            'mazda': ['mazda'],
            'subaru': ['subaru'],
            'mitsubishi': ['mitsubishi'],
            'suzuki': ['suzuki'],
            'kia': ['kia'],
            'hyundai': ['hyundai'],
            'volkswagen': ['volkswagen', 'vw'],
            'volvo': ['volvo'],
            'jaguar': ['jaguar'],
            'land rover': ['land rover'],
            'range rover': ['range rover'],
            'jeep': ['jeep'],
            'chevrolet': ['chevrolet', 'chevy'],
            'ford': ['ford'],
            'dodge': ['dodge'],
            'chrysler': ['chrysler'],
            'cadillac': ['cadillac'],
            'lincoln': ['lincoln'],
            'buick': ['buick'],
            'pontiac': ['pontiac'],
            'oldsmobile': ['oldsmobile'],
            'saturn': ['saturn'],
            'hummer': ['hummer'],
            'saab': ['saab'],
            'scion': ['scion'],
            'acura': ['acura'],
            'infiniti': ['infiniti'],
            'genesis': ['genesis'],
            'mini': ['mini'],
            'smart': ['smart'],
            'fiat': ['fiat'],
            'alfa romeo': ['alfa romeo'],
            'maserati': ['maserati'],
            'lancia': ['lancia'],
            'renault': ['renault'],
            'peugeot': ['peugeot'],
            'citroen': ['citroen'],
            'opel': ['opel'],
            'vauxhall': ['vauxhall'],
            'seat': ['seat'],
            'skoda': ['skoda'],
            'dacia': ['dacia'],
            'lada': ['lada'],
            'tata': ['tata'],
            'mahindra': ['mahindra'],
            'maruti': ['maruti'],
            'byd': ['byd'],
            'geely': ['geely'],
            'haval': ['haval'],
            'great wall': ['great wall'],
            'chery': ['chery'],
            'jac': ['jac'],
            'soueast': ['soueast'],
            'dongfeng': ['dongfeng'],
            'faw': ['faw'],
            'baic': ['baic'],
            'changan': ['changan'],
            'gac': ['gac'],
            'saic': ['saic'],
            'roewe': ['roewe'],
            'mg': ['mg'],
            'maxus': ['maxus'],
            'lynk & co': ['lynk & co'],
            'nio': ['nio'],
            'xpeng': ['xpeng'],
            'li auto': ['li auto'],
            'haima': ['haima'],
            'zotye': ['zotye'],
            'landwind': ['landwind'],
            'jmev': ['jmev'],
            'enovate': ['enovate'],
            'aiways': ['aiways'],
            'arcfox': ['arcfox'],
            'bordrin': ['bordrin'],
            'byd': ['byd'],
            'changhe': ['changhe'],
            'chery': ['chery'],
            'dearcc': ['dearcc'],
            'dengfeng': ['dengfeng'],
            'dongfeng': ['dongfeng'],
            'faw': ['faw'],
            'foton': ['foton'],
            'gac': ['gac'],
            'geely': ['geely'],
            'great wall': ['great wall'],
            'haima': ['haima'],
            'haval': ['haval'],
            'hongqi': ['hongqi'],
            'jac': ['jac'],
            'jetour': ['jetour'],
            'jonway': ['jonway'],
            'kawei': ['kawei'],
            'landwind': ['landwind'],
            'leapmotor': ['leapmotor'],
            'li auto': ['li auto'],
            'lynk & co': ['lynk & co'],
            'maxus': ['maxus'],
            'mg': ['mg'],
            'nio': ['nio'],
            'roewe': ['roewe'],
            'saic': ['saic'],
            'soueast': ['soueast'],
            'swm': ['swm'],
            'tank': ['tank'],
            'venucia': ['venucia'],
            'wey': ['wey'],
            'xpeng': ['xpeng'],
            'zotye': ['zotye']
        }

    def optimize_image(self, image_file):
        """Optimize image for better logo detection and car analysis"""
        try:
            # Read image
            image = Image.open(image_file)
            
            # Convert to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply adaptive histogram equalization
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Convert back to RGB
            enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(enhanced_rgb)
            
            # Save to bytes
            img_byte_arr = io.BytesIO()
            enhanced_image.save(img_byte_arr, format='JPEG', quality=95)
            img_byte_arr.seek(0)
            
            return img_byte_arr
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return image_file

    def detect_logo(self, image_file):
        """Detect car logo in image using YOLO"""
        try:
            if not self.logo_model:
                logger.warning("YOLO model not loaded, skipping logo detection")
                return None, None

            # Read image
            image = Image.open(image_file)
            
            # Run YOLO detection with confidence threshold
            results = self.logo_model(image, conf=0.5)  # Set minimum confidence threshold
            
            # Process results
            for result in results:
                boxes = result.boxes
                if len(boxes) == 0:
                    continue
                    
                # Get the highest confidence detection
                best_box = max(boxes, key=lambda x: float(x.conf[0]))
                cls = int(best_box.cls[0])
                class_name = result.names[cls]
                
                # Check if detected object matches any car brand
                for brand, keywords in self.car_brands.items():
                    if any(keyword in class_name.lower() for keyword in keywords):
                        # Get bounding box
                        x1, y1, x2, y2 = map(int, best_box.xyxy[0])
                        
                        # Crop image to logo region with padding
                        padding = 50
                        x1 = max(0, x1 - padding)
                        y1 = max(0, y1 - padding)
                        x2 = min(image.width, x2 + padding)
                        y2 = min(image.height, y2 + padding)
                        
                        logo_crop = image.crop((x1, y1, x2, y2))
                        
                        return brand, logo_crop
                        
            return None, None
            
        except Exception as e:
            logger.error(f"Error detecting logo: {e}")
            return None, None

    def encode_image(self, image_file):
        """Encode image to base64"""
        try:
            if not image_file:
                logger.error("No image file provided")
                return None, "Vui lòng chọn ảnh để phân tích"

            # Check if file is valid
            if not hasattr(image_file, 'read'):
                logger.error("Invalid image file object")
                return None, "File ảnh không hợp lệ"

            # Reset file pointer
            try:
                image_file.seek(0)
            except Exception as e:
                logger.error(f"Cannot seek image file: {e}")
                return None, "Không thể đọc file ảnh"
            
            # Read image content
            try:
                image_content = image_file.read()
                if not image_content:
                    logger.error("Empty image file")
                    return None, "File ảnh trống"
                
                # Create a new BytesIO object with the image content
                image_io = io.BytesIO(image_content)
                
                # Verify image can be opened
                try:
                    img = Image.open(image_io)
                    img.verify()  # Verify it's a valid image
                    image_io.seek(0)  # Reset after verify
                    
                    # Try to load the image to ensure it's not corrupted
                    img = Image.open(image_io)
                    img.load()
                    image_io.seek(0)
                    
                    # Check image dimensions
                    width, height = img.size
                    if width < 100 or height < 100:
                        logger.error("Image too small")
                        return None, "Ảnh quá nhỏ, vui lòng chọn ảnh lớn hơn"
                    if width > 4000 or height > 4000:
                        logger.error("Image too large")
                        return None, "Ảnh quá lớn, vui lòng chọn ảnh nhỏ hơn"
                    logger.info("Successfully verified and loaded image")
                except Exception as e:
                    logger.error(f"Invalid or corrupted image file: {e}")
                    return None, "File ảnh bị hỏng hoặc không hợp lệ"

                # Optimize image
                try:
                    optimized_image = self.optimize_image(image_io)
                    if optimized_image:
                        image_io = optimized_image
                        logger.info("Successfully optimized image")
                except Exception as e:
                    logger.error(f"Error optimizing image: {e}")
                    image_io.seek(0)

                # Detect logo
                try:
                    brand, logo_crop = self.detect_logo(image_io)
                    if logo_crop:
                        img_byte_arr = io.BytesIO()
                        logo_crop.save(img_byte_arr, format='JPEG', quality=95)
                        img_byte_arr.seek(0)
                        image_io = img_byte_arr
                        logger.info("Successfully detected and cropped logo")
                except Exception as e:
                    logger.error(f"Error detecting logo: {e}")
                    image_io.seek(0)

                # Ensure file pointer is at start
                image_io.seek(0)
                
                # Encode to base64
                try:
                    image_bytes = image_io.read()
                    if not image_bytes:
                        logger.error("No image data to encode")
                        return None, "Không thể đọc dữ liệu ảnh"
                    
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    if not base64_image:
                        logger.error("Failed to encode image to base64")
                        return None, "Không thể xử lý ảnh"
                    
                    logger.info(f"Successfully encoded image to base64, length: {len(base64_image)}")
                    return base64_image, None
                except Exception as e:
                    logger.error(f"Error encoding to base64: {e}")
                    return None, "Lỗi khi xử lý ảnh"
                
            except Exception as e:
                logger.error(f"Error reading image file: {e}")
                return None, "Không thể đọc file ảnh"
                
        except Exception as e:
            logger.error(f"Unexpected error in encode_image: {e}")
            return None, "Lỗi không mong muốn khi xử lý ảnh"
        finally:
            # Ensure files are closed
            try:
                if hasattr(image_file, 'close'):
                    image_file.close()
                if 'image_io' in locals() and hasattr(image_io, 'close'):
                    image_io.close()
            except:
                pass 