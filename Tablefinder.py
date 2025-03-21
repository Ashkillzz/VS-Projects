import cv2
import pytesseract
from pdf2image import convert_from_path
import numpy as np
import os

# Set the path to the Tesseract-OCR executable
pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

def pdf_to_images(pdf_path):
    """Convert PDF pages to images."""
    images = convert_from_path(pdf_path)
    return images

def find_table_dimensions(image):
    """Find table-like structures in the image using Tesseract."""
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Preprocess the image (binarization)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    
    # Detect contours in the image
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Analyze contours and extract bounding boxes for tables
    table_dimensions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Adjust these values based on your table size requirements
        if w > 50 and h > 20:  
            table_dimensions.append((x, y, w, h))
    return table_dimensions

def save_bounded_tables(image, table_dimensions, output_folder, page_number):
    """Save bounded table areas as separate images."""
    for idx, (x, y, w, h) in enumerate(table_dimensions):
        # Crop the bounded area
        cropped_image = image[y:y+h, x:x+w]
        
        # Save the cropped image
        output_path = os.path.join(output_folder, f"page_{page_number}_table_{idx + 1}.png")
        cv2.imwrite(output_path, cropped_image)
        print(f"Saved table as: {output_path}")

def process_pdf(pdf_path, output_folder):
    """Process a PDF and extract table dimensions."""
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    images = pdf_to_images(pdf_path)
    for page_number, image in enumerate(images, start=1):
        # Convert PIL image to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Find table dimensions
        table_dimensions = find_table_dimensions(cv_image)
        print(f"Page {page_number}: Found {len(table_dimensions)} tables.")
        
        # Save the bounded table areas
        save_bounded_tables(cv_image, table_dimensions, output_folder, page_number)

# Set the path to the PDF file and output folder
pdf_path = 'D:\Aswin\VS Projects\Assiduus_SFS1.pdf'
output_folder = 'Table Images'

# Process the PDF and save the tables
process_pdf(pdf_path, output_folder)
