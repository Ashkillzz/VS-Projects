import layoutparser as lp
import cv2
import numpy as np
import pytesseract
import json
from pdf2image import convert_from_path
from PIL import Image

# Load a pre-trained layout detection model
model = lp.Detectron2LayoutModel(
    "lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config",
    extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5], 
    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"}
)

def process_pdf(pdf_path, output_json, dpi=300):
    """
    Process a scanned PDF, detect layout elements, extract text, and save structured JSON.
    """
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=dpi)

    results = []
    
    for page_num, image in enumerate(images):
        print(f"Processing Page {page_num + 1}...")
        
        # Convert PIL image to OpenCV format
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Detect layout elements
        layout = model.detect(img)

        page_data = {"page": page_num + 1, "elements": []}

        for block in layout:
            x1, y1, x2, y2 = map(int, block.coordinates)
            cropped_img = image.crop((x1, y1, x2, y2))  # Crop the detected region

            # OCR - Extract text from the detected layout element
            text = pytesseract.image_to_string(cropped_img).strip()

            page_data["elements"].append({
                "type": block.type,
                "text": text,
                "coordinates": [x1, y1, x2, y2]
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
