import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

# Set your Hugging Face token
HF_TOKEN = "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"

# Load Mistral-7B-v0.1 model & tokenizer from Hugging Face Hub
model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name, token=HF_TOKEN)
model = AutoModelForCausalLM.from_pretrained(
    model_name, 
    torch_dtype=torch.float16, 
    device_map="auto", 
    use_auth_token=HF_TOKEN
)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF using OCR."""
    images = convert_from_path(pdf_path)
    text = "\n".join([pytesseract.image_to_string(img) for img in images])
    return text.strip()

def process_text_with_mistral(text):
    """Processes extracted text using Mistral-7B."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=4096)
    inputs = {k: v.to("cuda") for k, v in inputs.items()}  # Send inputs to GPU if available
    
    with torch.no_grad():
        output = model.generate(**inputs, max_length=4096)

    return tokenizer.decode(output[0], skip_special_tokens=True)

def save_to_json(data, output_path):
    """Saves extracted data to JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    pdf_path = "D:\Aswin\VS Projects\Assiduus_SFS1.pdf"  # Replace with your actual PDF file
    output_json = "LLM.json"

    extracted_text = extract_text_from_pdf(pdf_path)
    processed_text = process_text_with_mistral(extracted_text)

    data = {"extracted_text": extracted_text, "processed_text": processed_text}
    save_to_json(data, output_json)

    print(f"JSON saved at {output_json}")
