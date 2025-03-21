from pdf2image import convert_from_path
from rapidocr import RapidOCR
import os

def extract_text_from_pdf(pdf_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path, dpi=300)  # Adjust DPI for better accuracy
    ocr = RapidOCR()
    
    extracted_text = []
    
    for i, image in enumerate(images):
        result = ocr(image)  # Returns a RapidOCROutput object
        
        # Ensure results exist before processing
        if result:
            page_text = "\n".join([text for text, _, _ in result])  # Extract text from results
        else:
            page_text = "No text detected"

        extracted_text.append(f"Page {i+1}:\n{page_text}\n" + "-"*50)
    
    return "\n".join(extracted_text)

# Example usage
pdf_file = "D:\Aswin\VS Projects\Assiduus_SFS1.pdf"
text_output = extract_text_from_pdf(pdf_file)

# Save the output to a file
output_file = "RapidOCR.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(text_output)

print(f"Text extracted and saved to {output_file}")
