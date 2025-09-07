from PIL import Image, ImageGrab, ImageFilter
import pytesseract
import numpy as np
import cv2
import os
import time



def scan_image(image, weapon_type='pointdefense', settings=None):
    
    # Convert image to grayscale if needed
    if settings['grayscale'] or settings.get('use_adaptive_threshold', False):
        image = image.convert("L")
        print("Converted image to grayscale")

    # Apply thresholding if enabled
    if settings.get('use_adaptive_threshold', False):
        # Convert PIL image to numpy array for OpenCV
        img_array = np.array(image)
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        img_array = clahe.apply(img_array)
        
        # Simple binary threshold - for clean UI screenshots this works better than adaptive

        _, thresh = cv2.threshold(
            img_array,
            settings.get('threshold', 127),  # threshold value
            settings.get('threshold_max', 255),  # max value
            cv2.THRESH_BINARY
        )
        
        # Add slight blur to smooth any rough edges
        thresh = cv2.GaussianBlur(thresh, (3,3), 0)
        
        # Sharpen the result
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        thresh = cv2.filter2D(thresh, -1, kernel)
        
        # Convert back to PIL Image
        image = Image.fromarray(thresh)
        print("Applied optimized thresholding for UI screenshots")

    # Scale up small images for better OCR accuracy if enabled
    min_size = settings.get('min_size', 600)
    if settings['auto_scale'] and (image.height < min_size or image.width < min_size):
        scale_factor = settings['scale_factor']
        print(f"Image size: {image.size} - Scaling up by factor {scale_factor} for better OCR accuracy (minimum size: {min_size}px)") 
        new_width = int(image.width * scale_factor)
        new_height = int(image.height * scale_factor)
        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"Scaled image size: {image.size}")
    
    # Save the processed image if enabled
    if settings.get('save_images', False):
        try:
            # Create processed_images directory if it doesn't exist
            os.makedirs('processed_images', exist_ok=True)
            
            # Generate a unique filename with timestamp
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'processed_images/processed_{timestamp}.png'
            
            # Save the image
            image.save(filename)
            print(f"Saved processed image to: {filename}")
        except Exception as e:
            print(f"Error saving processed image: {str(e)}")
    
    # Extract text from image using pytesseract with configured PSM mode
    config = f"--psm {settings['psm_mode']}"
    text = pytesseract.image_to_string(image, config=config)
    print("Processing " + weapon_type)
    print("Extracted text from image:")
    print("---START OF TEXT---")
    print(text)
    print("---END OF TEXT---")
    
    return text