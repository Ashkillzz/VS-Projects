import os
import json
import ollama
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

# Function to extract text from searchable PDFs
def extract_text_from_pdf(pdf_path):
    extracted_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n\n"
    return extracted_text.strip()

# Function to extract text from scanned PDFs using OCR
def extract_text_from_scanned_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text_data = [pytesseract.image_to_string(img) for img in images]
    return "\n".join(text_data)

# Function to process text with DeepSeek R1 1.5B (via Ollama)
def extract_json_with_deepseek(text):
    prompt = f"""
    Extract structured information from the following document and return a valid JSON response.

    --- DOCUMENT TEXT START ---

    {text}
    
    --- DOCUMENT TEXT END ---
    """

    response = ollama.chat(model="deepseek-r1:1.5b", messages=[{"role": "user", "content": prompt}])
    structured_json = response["message"]["content"]
    print(structured_json)

    try:
        json_data = json.loads(structured_json)  # Ensure valid JSON
    except json.JSONDecodeError:
        json_data = {"error": "Invalid JSON format from DeepSeek R1 1.5B"}

    return json_data

if __name__ == '__main__':
    pdf_path = r'D:\Aswin\VS Projects\Files\PDF Files\StandaloneFS(BS_PL).pdf'  # PDF file path
    json_output_path = "DeepSeek1.5b.json"
    
    # Extract text from PDF (scanned or searchable)
    extracted_text = extract_text_from_scanned_pdf(pdf_path)
    print("Text extracted from PDF\n\n", extracted_text,"\n\n")
    
    # Process extracted text using DeepSeek R1 1.5B model
    structured_data = extract_json_with_deepseek(extracted_text)
    
    # Save structured JSON output
    with open(json_output_path, 'w') as file:
        json.dump(structured_data, file, indent=4)
    
    print(f"JSON output saved to {json_output_path}")
