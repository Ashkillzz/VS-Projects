import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image

def flatten_xfa_pdf(input_pdf, output_pdf, dpi=300):
    """
    Flattens an XFA PDF by rendering each page as an image and saving it as a new standard PDF.
    
    :param input_pdf: Path to the input XFA PDF.
    :param output_pdf: Path to the output flattened PDF.
    :param dpi: Resolution for image conversion (higher = better quality, larger file).
    """
    # Convert PDF pages to images
    images = convert_from_path(input_pdf, dpi=dpi)
    
    # Create a new PDF
    pdf_writer = fitz.open()

    for img in images:
        img_bytes = img.convert("RGB").tobytes("jpeg", "RGB")
        img_pixmap = fitz.Pixmap(fitz.csRGB)
        page = pdf_writer.new_page(width=img_pixmap.width, height=img_pixmap.height)
        page.insert_image(page.rect, pixmap=img_pixmap)
    
    # Save the flattened PDF
    pdf_writer.save(output_pdf)
    pdf_writer.close()
    print(f"Flattened PDF saved as: {output_pdf}")

# Example usage
flatten_xfa_pdf("D:\Aswin\VS Projects\AOC Forms\[05-11-2022]_Form_AOC-4-05112022_signed_3.pdf", "output_flattened.pdf")
