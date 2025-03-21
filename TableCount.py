import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

# Path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

# List of table name phrases
table_name_phrases = ["Balance Sheet", "Statement Of Profit and Loss"]  # Update as needed

def extract_text_from_table(image, table_bbox):
    """
    Extracts text from a specific table region (bounding box) in an image.
    Returns the extracted text line by line.
    """
    x, y, w, h = table_bbox
    table_region = image[y:y+h, x:x+w]
    # Use Tesseract to extract text
    table_text = pytesseract.image_to_string(table_region, config="--psm 6")
    return table_text.strip().split("\n")

def find_tables_and_extract_text(image):
    """
    Detects tables in an image, extracts their contents,
    and filters by table name phrases.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Detect horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

    # Combine lines to detect table structures
    table_mask = cv2.add(horizontal_lines, vertical_lines)
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    table_data = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 100 and h > 50:  # Heuristic for table dimensions
            # Extract text from the detected table region
            table_text_lines = extract_text_from_table(image, (x, y, w, h))
            # Check if table name matches the specified phrases
            if any(phrase.lower() in " ".join(table_text_lines).lower() for phrase in table_name_phrases):
                table_data.append({
                    "bounding_box": (x, y, w, h),
                    "content": table_text_lines,
                })

    return table_data

def extract_tables_from_pdf(pdf_path, output_txt):
    """
    Extracts contents of tables matching specified phrases from a PDF.
    """
    images = convert_from_path(pdf_path)
    all_table_data = []

    for page_number, image in enumerate(images, start=1):
        # Convert PIL image to OpenCV format
        open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        page_table_data = find_tables_and_extract_text(open_cv_image)
        for table in page_table_data:
            table["page"] = page_number
        all_table_data.extend(page_table_data)
        print(type(all_table_data))

    print(all_table_data)

    '''if output_txt:
        with open(all_table_data, 'w', encoding='utf-8') as txt_file:
            txt_file.writelines(all_table_data)'''

    '''if output_txt:
        with open(output_txt, 'w', encoding='utf-8') as txt_file:
            for item in all_table_data:
                txt_file.write(item)
'''
    return

# Main program
if __name__ == "__main__":
    pdf_path = "StandaloneFSsigned.pdf"  # Replace with the path to your PDF
    output_txt = "output.txt" 
    extract_tables_from_pdf(pdf_path, output_txt)

    for table in tables:
        print(f"Page {table['page']}, Bounding Box: {table['bounding_box']}")
        print("Table Content:")
        
