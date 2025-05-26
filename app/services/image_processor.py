import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        # Load YOLO model for logo detection
        self.model = cv2.dnn.readNetFromDarknet(
            "yolov8n.pt",
            "yolov8n.cfg"
        )
        
    def encode_image(self, image_file) -> Optional[str]:
        """
        Encode image to base64 string
        
        Args:
            image_file: File object containing the image
            
        Returns:
            str: Base64 encoded image string
        """
        try:
            # Read image file
            image_bytes = image_file.read()
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Resize if too large
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return img_str
            
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            return None
            
    def detect_logo(self, image_file) -> Tuple[Optional[str], Optional[np.ndarray]]:
        """
        Detect car logo in image using YOLO
        
        Args:
            image_file: File object containing the image
            
        Returns:
            Tuple[str, np.ndarray]: Detected brand name and cropped logo image
        """
        try:
            # Read image
            image_bytes = image_file.read()
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.error("Failed to decode image")
                return None, None
                
            # Get image dimensions
            height, width = img.shape[:2]
            
            # Prepare image for YOLO
            blob = cv2.dnn.blobFromImage(
                img, 
                1/255.0, 
                (416, 416), 
                swapRB=True, 
                crop=False
            )
            
            # Set input and run forward pass
            self.model.setInput(blob)
            layer_names = self.model.getLayerNames()
            output_layers = [layer_names[i - 1] for i in self.model.getUnconnectedOutLayers()]
            outputs = self.model.forward(output_layers)
            
            # Process detections
            class_ids = []
            confidences = []
            boxes = []
            
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > 0.5:  # Confidence threshold
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        
                        x = int(center_x - w/2)
                        y = int(center_y - h/2)
                        
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            
            # Apply non-maximum suppression
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            
            if len(indices) > 0:
                # Get the best detection
                idx = indices[0]
                box = boxes[idx]
                x, y, w, h = box
                
                # Crop logo region
                logo_crop = img[y:y+h, x:x+w]
                
                # Map class ID to brand name
                brand = self._get_brand_name(class_ids[idx])
                
                return brand, logo_crop
                
            return None, None
            
        except Exception as e:
            logger.error(f"Error detecting logo: {str(e)}")
            return None, None
            
    def _get_brand_name(self, class_id: int) -> str:
        """
        Map YOLO class ID to brand name
        
        Args:
            class_id: YOLO class ID
            
        Returns:
            str: Brand name
        """
        # Map of class IDs to brand names
        brand_map = {
            0: "Ferrari",
            1: "Lamborghini",
            2: "Porsche",
            3: "BMW",
            4: "Mercedes",
            5: "Audi",
            6: "Toyota",
            7: "Honda",
            8: "Ford",
            9: "Chevrolet"
        }
        
        return brand_map.get(class_id, "Unknown") 