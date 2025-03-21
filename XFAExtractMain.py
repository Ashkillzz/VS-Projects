import os
import re
import pikepdf


class XfaObj(dict):
    def __init__(self, source_pdf):  
        self.source = source_pdf    ## Storing PDF obj in self.source
        self.root = self.source.Root.AcroForm.XFA   ## Navigates to XFA form data
        self.xfa_dict = {}  ## To store XFA data
        
        for i, item in enumerate(self.root):
            if i % 2 == 0 and isinstance(item, pikepdf.String):    ## Represents a label if condition is true
                label = str(item)
                self.xfa_dict[label] = self.root[i + 1]     ## label = key, next item is the value
        
        super(XfaObj, self).__init__(self.xfa_dict)     ## Initializes dict with processed XFA data

    def __getitem__(self, key):     
        if isinstance(self.xfa_dict[key], pikepdf.Stream):      ## To check whether value in dict keys are pikepdf.Stream objects 
            return self.xfa_dict[key].read_bytes().decode('utf-8')
        else:
            print('XFA item detected was not a stream')
            return self.xfa_dict[key]

    def __setitem__(self, key, value):
        if isinstance(value, str):      ## To check if value set is a string
            value = bytes(value, 'utf-8')
        self.xfa_dict[key].write(value)

def extract_xfa(file_name):
    with pikepdf.Pdf.open(file_name) as pdf_data:
        xfa_dict = XfaObj(pdf_data)
        folder_name = re.sub(r'\.pdf$', '', os.path.basename(file_name))
        
        os.makedirs(folder_name, exist_ok=True)  ## Creates a new folder in the name of the PDF file processed

        for key in xfa_dict.keys():
            out_file = re.sub(r'[<>: ]', '', key)
            out_file = re.sub(r'/', 'END', out_file)
            if out_file == 'datasets':
                full_path = os.path.join(folder_name, f"{out_file}.xml") ## Saving xml files into folder in provided path\
                with open(full_path, 'w', encoding="utf-8") as f:
                    f.write(xfa_dict[key])
        print(f"Extracted XFA contents to folder: {folder_name}")

if __name__ == "__main__":

    file_path = input("\nEnter the path to the PDF file: ").strip()  
    if not os.path.exists(file_path):  ## Exit if file not found in provided path
        print(f"File not found: {file_path}")
        exit()

    extract_xfa(file_path)
