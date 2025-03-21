import win32com.client

def export_pdf_to_xml(pdf_path, xml_path):
    try:
        # Create Acrobat App Object
        avDoc = win32com.client.Dispatch("AcroExch.AVDoc")
        
        # Open the PDF file
        if not avDoc.Open(pdf_path, ""):
            print("Failed to open PDF.")
            return False
        
        # Get the PDDoc object
        pdDoc = avDoc.GetPDDoc()
        
        # Export as XML
        jso = pdDoc.GetJSObject()
        jso.saveAs(xml_path, "com.adobe.acrobat.xml")
        
        # Close document
        avDoc.Close(True)
        
        print(f"PDF successfully exported to XML: {xml_path}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# Example Usage
pdf_file = r"D:\Aswin\VS Projects\AOC Forms\[14-12-2023]_Form_AOC-4-14122023_signed_0.pdf"
xml_file = r"new.xml"

export_pdf_to_xml(pdf_file, xml_file)
