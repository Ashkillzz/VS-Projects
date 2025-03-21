from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np

# Set path to your Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

def preprocess_image(image):
    """
    Convert image to grayscale and apply thresholding.
    """
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return binary

def enhance_image(image):
    """
    Enhance image quality by removing noise, applying adaptive thresholding,
    and increasing contrast to improve OCR accuracy.
    """
    image = cv2.fastNlMeansDenoising(image, h=10)
    image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Increase contrast
    alpha = 1.5  # Contrast control
    beta = 0  # Brightness control
    image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    
    return image

def correct_orientation(image):
    """
    Detect and correct the orientation of the image.
    """
    osd = pytesseract.image_to_osd(image)
    rotate_angle = int(osd.split('\n')[1].split(':')[-1].strip())
    
    if rotate_angle == 90:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rotate_angle == 180:
        image = cv2.rotate(image, cv2.ROTATE_180)
    elif rotate_angle == 270:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    
    return image

def pdf_to_text(pdf_path, output_txt=None):
    """
    Extracts text from all pages of the PDF document with orientation correction and image enhancement.

    Args:
        pdf_path: Path to the PDF file.
        output_txt: Path to the output TXT file (optional).

    Returns:
        A list of strings, where each string represents the extracted text from a page.
    """
    images = convert_from_path(pdf_path)
    all_text = []

    for i, image in enumerate(images):
        processed_image = preprocess_image(image)
        enhanced_image = enhance_image(processed_image)
        corrected_image = correct_orientation(enhanced_image)
        text = pytesseract.image_to_string(corrected_image, config='--psm 6')
        all_text.append(f"\n\n--- Page {i+1} ---\n{text}\n")

    # Save the extracted text to a TXT file (optional)
    if output_txt:
        with open(output_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.writelines(all_text)

    return all_text

# Example usage
pdf_path = "D:\Aswin\VS Projects\MCA Doc\HarwestWild Financials and Auditor Report.pdf"  # Replace with the path to your scanned PDF 
output_txt = "D:\Aswin\VS Projects\FullOCR.txt"  # Replace with the desired output TXT file name
extracted_text = pdf_to_text(pdf_path, output_txt)
print("Extracted text saved to:", output_txt)
