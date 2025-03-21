import fitz  # PyMuPDF (for checking if PDF is image-based)
import pytesseract  # For OCR
from PIL import Image  # For image handling
import requests
import json
import re
from transformers import pipeline

# 1. Hugging Face Setup (replace with your token)
HF_ACCESS_TOKEN = "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"  # Replace with your actual token
API_URL = "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-r1-7b-distill"

# 2. OCR (if needed - handle images/scanned PDFs separately)
def pdf_to_text(pdf_path):
    """Extracts text from a PDF, handling OCR for scanned PDFs."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            if page.is_image: # Check if the page is an image (scanned PDF)
                pix = page.get_pixmap() # Get image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img) # OCR with Tesseract
            else:
                text += page.get_text() # Regular text extraction
        return text
    except fitz.FileNotFoundError:
        return "Error: PDF file not found."
    except Exception as e:
        return f"An unexpected error occurred: {e}"


def clean_ocr_text(text):
    """Basic OCR text cleaning (customize as needed)."""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('\x0c', '')  # Form feed
    # ... Add more cleaning rules as needed ...
    return text


def extract_json_from_llm_response(llm_output):
    """Extracts JSON from LLM response, handling variations."""
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


# 3. LLM Interaction (DeepSeek via Hugging Face Inference API)
def llm_request(text, prompt_template):
    """Sends request to DeepSeek model via Hugging Face Inference API."""
    headers = {"Authorization": f"Bearer {HF_ACCESS_TOKEN}"}
    prompt = prompt_template.format(text=text) # Format the prompt
    payload = {"inputs": prompt}  # Correct payload format for HF Inference API

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        llm_output = response.json()[0]["generated_text"] # Extract the generated text
        return llm_output
    except requests.exceptions.RequestException as e:
        return f"Error communicating with HF API: {e}\nResponse: {response.text if hasattr(response, 'text') else None}"
    except (KeyError, IndexError) as e:
        return f"Unexpected response format from HF API: {e}\nResponse: {response.text if hasattr(response, 'text') else None}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# 4. Main Function
def process_pdf_to_json(pdf_path, prompt_template):
    """Orchestrates PDF to JSON conversion."""

    text_or_error = pdf_to_text(pdf_path) # Extract text
    if isinstance(text_or_error, str) and text_or_error.startswith("Error"): # Check for errors
        return text_or_error

    cleaned_text = clean_ocr_text(text_or_error) # Clean the extracted text
    llm_response = llm_request(cleaned_text, prompt_template)  # Send to LLM
    
    if isinstance(llm_response, str) and llm_response.startswith("Error"): # Check for errors
        return llm_response
    
    json_output = extract_json_from_llm_response(llm_response) # Extract JSON
    return json_output



# 5. Example Usage
pdf_file = "D:\Aswin\VS Projects\Files\PDF Files\StandaloneFS(BS_PL).pdf"

prompt_template = """
Extract the following information from the text below and format it as JSON:
Name (string), Age (integer), City (string), Email (string).

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



