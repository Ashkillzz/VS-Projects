import pytesseract
from pdf2image import convert_from_path

def extract_content_from_pdf(pdf_path, phrase_dict, output_file):
    # Convert PDF pages to images
    images = convert_from_path(pdf_path)

    extracted_content = ""

    for page_number, image in enumerate(images, start=1):

        text = pytesseract.image_to_string(image)
        for start_phrase, end_phrase in phrase_dict.items():
            # Search for start and end phrases
            start_index = text.find(start_phrase)
            end_index = text.find(end_phrase, start_index)

            if start_index != -1 and end_index != -1:
                # Extract content between start and end phrases
                content = text[start_index + len(start_phrase):end_index].strip()
                extracted_content += f"\nPage {page_number}:\n{content}\n\n"

        print("\n\n")

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(extracted_content)

    print(f"Extracted content saved to {output_file}")


def field_match(out):
    print("\nYes")


if __name__ == "__main__":

    pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'

    pdf_path = "StandaloneFSsigned.pdf"

    '''Equ_Liab = {
        "Share capital" : "sc",
        "Reserves and surplus" : "ras",
        "Long-term provisions" : "ltp",
        "Long-term borrowings" : "ltb",
        "Dues of micro enterprises and small enterprises" : "dmese",
        "other than micro enterprises and small enterprises" : "domese",
        "Short-term borrowings" : "stb",
        "Short-term provisions" : "stp",
        "Other current liabilities" : "ocl",
        "TOTAL" : "tl",
    }

    Assets ={
        "Property, plant & equipment" : "ppe",
        "Intangible assets" : "ia",
        "Intangible assets under development (IAUD)" : "iaud",
        "Deferred tax asset (Net)" : "dta",
        "Non-current investments" : "nci",
        "Other non- current asset" : "onca",
        "Inventories" : "inv",
        "Trade receivables" : "tr",
        "Cash and cash equivalents" : "cace",
        "Short-term loans and advances" : "stla",
        "Other current assets" : "oca",
        "Total" : "tl" 
    }'''


    phrase_dict = {
        "Balance Sheet": "Company overview & significant accounting policies",
        "Statement of Profit and Loss": "Company overview & significant accounting policies"
    }

    output_file = "Content.txt"

    extract_content_from_pdf(pdf_path, phrase_dict, output_file)
    field_match(output_file)


