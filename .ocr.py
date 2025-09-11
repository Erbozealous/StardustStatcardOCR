from PIL import Image, ImageGrab, ImageFilter
import pytesseract
from pytesseract import Output
import numpy as np
import cv2
import os
import time



def scan_image(image, weapon_type='pointdefense', settings=None):
    if settings is None:
        settings = {
            'grayscale': True,
            'use_adaptive_threshold': True,
            'threshold': 127,
            'threshold_max': 255,
            'auto_scale': True,
            'scale_factor': 2,
            'min_size': 600,
            'psm_mode': 6,  # Assume a single uniform block of text
            'save_images': False,
        }
    # Convert image to grayscale if needed
    if settings['grayscale'] or settings.get('use_adaptive_threshold', False):
        image = image.convert("L")
        print("Converted image to grayscale")

    # Apply thresholding if enabled
    if settings.get('use_adaptive_threshold', False):
        img = np.array(image)

        # Convert to RGB (OpenCV uses BGR by default)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Define background color in RGB
        bg_color = np.array([50, 50, 50])  # #323232

        # Create a mask for everything that is NOT the background
        mask = cv2.inRange(img_rgb, bg_color + 1, bg_color + 255)

        # Optional: invert mask so text is white, background is black
        mask_inv = cv2.bitwise_not(mask)

        # Apply mask to original image (or just use mask_inv for OCR)
        # text_only = cv2.bitwise_and(img_rgb, img_rgb, mask=mask_inv)

        # Convert to grayscale for Tesseract
        # gray = cv2.cvtColor(text_only, cv2.COLOR_RGB2GRAY)

        # Apply thresholding if needed
        # _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Convert back to PIL Image
        image = Image.fromarray(mask_inv)
        print("Applied optimized thresholding for UI screenshots")

    # Scale up small images for better OCR accuracy if enabled
    print(f"Image size: {image.size}")
    min_size = settings.get('min_size', 600)
    if settings['auto_scale'] and (image.height < min_size or image.width < min_size):
        scale_factor = settings['scale_factor']
        print(f"Scaling up by factor {scale_factor}") 
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
    text = pytesseract.image_to_string(image, lang="STARDUST", config="--tessdata-dir ./tessdata")
    print("Processing " + weapon_type)
    print("Extracted text from image:")
    print("---START OF TEXT---")
    print(text)
    print("---END OF TEXT---")


    return text
