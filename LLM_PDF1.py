from pdf2image import convert_from_path
import pytesseract
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
import json
import re
import torch  # Import torch

'''config = AutoConfig.from_pretrained("deepseek-ai/DeepSeek-R1", trust_remote_code=True)
del config.quantization_config

model = AutoModelForCausalLM.from_pretrained("deepseek-ai/DeepSeek-R1", config=config, trust_remote_code=True)'''

# Configuration
PDF_PATH = "D:\Aswin\VS Projects\Files\PDF Files\StandaloneFS(BS_PL).pdf"
OUTPUT_JSON = "D:\Aswin\VS Projects\DS1.json"
LLAMA_MODEL = "microsoft/Phi-3.5-mini-instruct"

def pdf_to_ocr_text(pdf_path):
    """Convert PDF to OCR text using Tesseract"""
    try:
        images = convert_from_path(pdf_path)
        full_text = ""
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image)
            full_text += f"Page {i+1}:\n{text}\n"
        return full_text
    except Exception as e:
        raise RuntimeError(f"PDF processing failed: {str(e)}")

def structure_with_deepseek(text, model, tokenizer):
    """Use the LLM  to structure OCR text into JSON format"""
    try:
        prompt = (
            "Analyze the following document text and structure it into JSON format. "
            "Identify key entities, sections, and relationships. "
            "Maintain hierarchical structure where appropriate.\n\n"
            f"DOCUMENT TEXT:\n{text}\n\n"
            "JSON STRUCTURE:"
        )

        inputs = tokenizer(prompt, return_tensors="pt", max_length=4096, truncation=True)

        # Check for CUDA availability and move inputs to device
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        model.to(device)  # Move the model to the same device

        with torch.no_grad(): # Important for inference
            outputs = model.generate(
                **inputs,
                max_new_tokens=2048,
                temperature=0.3,
                do_sample=True
            )

        raw_output = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # More robust JSON extraction using regex
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)  # Parse JSON
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON extracted: {e}")
                print(f"Raw Output: {raw_output}") # Print raw output for debugging
                return {} # Return empty dictionary to avoid crashing
        else:
            print("Warning: No JSON found in model output.")
            print(f"Raw Output: {raw_output}") # Print raw output for debugging
            return {}  # Return empty dictionary


    except Exception as e:
        raise RuntimeError(f"DeepSeek processing failed: {str(e)}")

if __name__ == "__main__":

    try:
        print("Started!!\n\n")
        # Initialize DeepSeek model, now with device placement
        tokenizer = AutoTokenizer.from_pretrained(LLAMA_MODEL, trust_remote_code=True)

        config = AutoConfig.from_pretrained("microsoft/Phi-3.5-mini-instruct", trust_remote_code=True)
        #del config.quantization_config

        model = AutoModelForCausalLM.from_pretrained("microsoft/Phi-3.5-mini-instruct", config=config, trust_remote_code=True)
        

        ocr_text = pdf_to_ocr_text(PDF_PATH)
        print("OCR Text Extracted Successfully")

        structured_data = structure_with_deepseek(ocr_text, model, tokenizer)

        with open(OUTPUT_JSON, 'w') as f:
            json.dump(structured_data, f, indent=2)

        print(f"Successfully saved structured JSON to {OUTPUT_JSON}")

    except Exception as e:
        print(f"An error occurred: {e}")  # Catch and print errors