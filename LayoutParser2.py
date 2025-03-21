import pytesseract
import json
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

def process_pdf(pdf_path, output_json, dpi=300):
    """
    Process a scanned PDF, extract text with bounding boxes, and save as JSON.
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)

    results = []
    
    for page_num, image in enumerate(images):
        print(f"Processing Page {page_num + 1}...")

        # Convert PIL image to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Perform OCR and extract bounding boxes
        ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        page_data = {"page": page_num + 1, "elements": []}

        for i in range(len(ocr_data["text"])):
            text = ocr_data["text"][i].strip()
            if text:  # Ignore empty text
                x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
                page_data["elements"].append({
                    "text": text,
                    "coordinates": [x, y, x + w, y + h]
                })

        results.append(page_data)

    # Save extracted data to JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"Processing complete! Output saved to {output_json}")

if __name__ == '__main__':

    PDF_path = r'D:\Aswin\VS Projects\Files\PDF Files\StandaloneFS(BS_PL).pdf'
    Json_file = r'LayoutParser.json'
    # Example usage
    process_pdf(PDF_path, Json_file)
