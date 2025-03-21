import fitz  # PyMuPDF (for checking if PDF is image-based)
import pytesseract  # For OCR
from PIL import Image  # For image handling
import google.generativeai as genai  # Google SDK for Gemini
import json
import re
import os

# 1. Gemini API Setup (replace with your API key)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyB-GXks57MkvGtvIgNz9RFFK6FfQBL6o8A")  # Use env variable if possible
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

import google.generativeai as genai
genai.configure(api_key="YOUR_GEMINI_API_KEY", transport="rest")  # Use REST instead of gRPC

def pdf_to_text(pdf_path):
    """Extracts text from a PDF, handling OCR for scanned PDFs."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            pix = page.get_pixmap()  # Get image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img)  # OCR with Tesseract
            
        return text
    except fitz.FileNotFoundError:
        return "Error: PDF file not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def clean_ocr_text(text):
    """Basic OCR text cleaning (customize as needed)."""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('\x0c', '')  # Form feed
    return text

def extract_json_from_llm_response(llm_output):
    try:
        return json.loads(llm_output)  # Direct JSON parsing
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", llm_output, re.DOTALL)  # Find JSON block
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass  # Fallback to more lenient parsing if needed
        return None  # Could not extract JSON

# 3. LLM Interaction using Google SDK (No direct API calls)
def gemini_request(text, prompt_template):
    """Sends request to Gemini model using Google's SDK."""
    try:
        model = genai.GenerativeModel("gemini-pro")  # Use Gemini Pro model
        prompt = prompt_template.format(text=text)
        
        response = model.generate_content(prompt)  # Generate response
        print("RAW RESPONSE:", response)  # Debugging output
        
        if response and response.text:
            return response.text  # Return extracted text response
        else:
            return f"Unexpected response format from Gemini API: {response}"
    except Exception as e:
        return f"An error occurred: {e}"

# 4. Main Function
def process_pdf_to_json(pdf_path, prompt_template):
    """Orchestrates PDF to JSON conversion using Gemini."""

    text_or_error = pdf_to_text(pdf_path)
    if isinstance(text_or_error, str) and text_or_error.startswith("Error"):
        return text_or_error

    cleaned_text = clean_ocr_text(text_or_error)
    llm_response = gemini_request(cleaned_text, prompt_template)  # Use gemini_request

    if isinstance(llm_response, str) and llm_response.startswith("Error"):
        return llm_response
    
    json_output = extract_json_from_llm_response(llm_response)
    return json_output

# 5. Example Usage
if __name__ == '__main__':
    pdf_file = "D:\Aswin\VS Projects\Files\PDF Files\StandaloneFS(BS_PL).pdf"  # Replace with your PDF file path 

    prompt_template = """
    Analyze the content and provide me strucutured data in JSON for the given OCR generated PDF text. 

    Text:
    {text}

    Return ONLY the JSON. Do not include any other text or explanations.
    """

    json_data = process_pdf_to_json(pdf_file, prompt_template)

    if isinstance(json_data, dict):
        print(json.dumps(json_data, indent=4))
        with open("output.json", "w") as f:
            json.dump(json_data, f, indent=4)
    elif isinstance(json_data, str):
        print(json_data)  # Print the error message
    else:
        print("No JSON data returned.")
