import os
from pdf2image import convert_from_path
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image

# Load TrOCR processor and model
processor = TrOCRProcessor.from_pretrained("microsoft/trocr-base-printed")
model = VisionEncoderDecoderModel.from_pretrained("microsoft/trocr-base-printed")

def pdf_to_images(pdf_path, dpi=300):
    """Convert PDF pages to images."""
    return convert_from_path(pdf_path, dpi=dpi)

def ocr_image(image):
    """Perform OCR on an image using TrOCR."""
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    generated_ids = model.generate(pixel_values)
    return processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

def process_pdf(pdf_path, output_txt_file):
    """Extract text from PDF and save it to a structured .txt file."""
    images = pdf_to_images(pdf_path)
    with open(output_txt_file, "w", encoding="utf-8") as txt_file:
        for i, image in enumerate(images):
            text = ocr_image(image)
            txt_file.write(f"===== Page {i+1} =====\n{text}\n\n")
    
    print(f"OCR completed. Extracted text saved to: {output_txt_file}")

# Input PDF file and output text file
pdf_file = "D:\Aswin\VS Projects\Assiduus_SFS1.pdf"   # Change this to your PDF file path
output_txt = "TrOCR.txt" # Output structured text file

# Process the PDF
process_pdf(pdf_file, output_txt)
