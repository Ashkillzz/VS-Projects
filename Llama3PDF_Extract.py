import os
import json
import ollama
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

# Initialize Flask App
app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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

# Function to process text with Llama 3 (via Ollama)
def extract_json_with_llama(text):
    prompt = f"""
    Extract structured information from the following document and return a valid JSON response.

    --- DOCUMENT TEXT START ---
    {text}
    --- DOCUMENT TEXT END ---

    Extracted JSON format:
    {{
        "title": "Extracted Title",
        "date": "YYYY-MM-DD",
        "author": "Author Name",
        "content": "Full document content",
        "tables": [
            {{"header": ["Column1", "Column2"], "rows": [["Row1Data1", "Row1Data2"], ["Row2Data1", "Row2Data2"]]}}
        ]
    }}
    """

    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
    structured_json = response["message"]["content"]

    try:
        json_data = json.loads(structured_json)  # Ensure valid JSON
    except json.JSONDecodeError:
        json_data = {"error": "Invalid JSON format from Llama 3"}

    return json_data

# API Endpoint to upload and process PDF
@app.route("/extract", methods=["POST"])
def extract():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save uploaded PDF
    filename = secure_filename(file.filename)
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(pdf_path)

    # Extract text
    extracted_text = extract_text_from_pdf(pdf_path)
    if not extracted_text:  # If no text found, try OCR
        extracted_text = extract_text_from_scanned_pdf(pdf_path)

    # Process with Llama 3 via Ollama
    json_output = extract_json_with_llama(extracted_text)

    return jsonify(json_output)

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
