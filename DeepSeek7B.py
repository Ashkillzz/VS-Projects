import pytesseract
import json
import ollama
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

def ocr_pdf_to_json(pdf_path, model="deepseek-r1:7b"):
    # Convert PDF to images
    images = convert_from_path(pdf_path)
    extracted_text = ""
    
    # Perform OCR on each image
    for img in images:
        text = pytesseract.image_to_string(img)
        extracted_text += text + "\n"

    print(extracted_text)

    # Process text using DeepSeek via Ollama
    response = ollama.chat(model=model, messages=[{"role": "user", "content": extracted_text}])
    '''[{"role": "user", "content": f"""Provide me a properly structured JSON from the OCR text extracted for the below provided extracted text data. Do not consider page headers or footers for JSON conversion. Only extract data contained under (Share Capital) and (Related Party Transactions or Disclosures) as JSON. ***Rules***\n1.You MUST respond ONLY in valid JSON format.\n2.No explanations, reasoning, or additional text.\n3.If data is missing, leave fields empty but maintain structure.\nExtracted Text :\n\n{extracted_text}"""}]'''
    processed_text = response["message"]["content"]
    
    # Convert processed text to JSON
    json_output = {"text": processed_text}
    return json_output

# Example usage
pdf_file = "D:\Aswin\VS Projects\Assiduus_SFS1.pdf"
result = ocr_pdf_to_json(pdf_file)

# Save to JSON file
with open("DS.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

print("OCR and processing complete. JSON saved to DS.json")
