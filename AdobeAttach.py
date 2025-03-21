import fitz  # PyMuPDF
import os

def extract_attachments(pdf_path, output_folder):
    doc = fitz.open(pdf_path)

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    for i in range(doc.embfile_count):  # Use embfile_count to get total attachments
        file_info = doc.embfile_info(i)  # Pass index i
        file_name = file_info['filename']
        file_data = doc.embfile_get(i)  # Extract the embedded file data

        with open(os.path.join(output_folder, file_name), "wb") as f:
            f.write(file_data)
        print(f"Extracted: {file_name}")

# Example usage
extract_attachments("D:\Aswin\VS Projects\Form AOC-4-28102024.pdf", "SignaAttachments")
