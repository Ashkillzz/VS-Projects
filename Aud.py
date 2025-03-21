from pdf2image import convert_from_path
import pytesseract
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure nltk resources are downloaded
nltk.download('stopwords')
nltk.download('wordnet')

# Path to the Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r'D:/Aswin/TesseractOCR/tesseract.exe'  # Adjust this path as needed

# Convert PDF to images
pdf_path = "Assiduus_Audit_Report_FY2022-23.pdf"  # Replace with your actual PDF path
pages = convert_from_path(pdf_path, 300, poppler_path="D:/Aswin/Poppler/Library/bin")  # 300 DPI for better OCR accuracy

# Initialize a variable to store the entire text
full_text = ""

# Define patterns to identify unwanted content (footers, signatures, etc.)
footer_pattern = re.compile(r'(Footer text pattern|Signature:|Page \d+)$', re.IGNORECASE)

# Initialize lemmatizer and stopwords
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Normalize text by converting to lowercase, removing punctuation, and lemmatizing."""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation
    words = text.split()
    words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]  # Lemmatize words and remove stopwords
    return ' '.join(words)

def clean_text(text):
    """Remove unwanted lines based on patterns."""
    cleaned_lines = []
    for line in text.split('\n'):
        if not footer_pattern.search(line):
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def extract_section(text, section_keyword):
    """Extract text for a specific section based on a keyword."""
    normalized_keyword = preprocess_text(section_keyword)
    lines = text.split('\n')
    
    # Find the section starting point
    start_index = -1
    for i, line in enumerate(lines):
        if normalized_keyword in preprocess_text(line):
            start_index = i
            break
    
    if start_index == -1:
        return ""
    
    # Extract text starting from the section keyword
    return '\n'.join(lines[start_index:])

def create_regex_from_keyword_lists(keyword_lists):
    """Create a regex pattern to match any of the keywords in each list."""
    pattern_parts = []
    
    for keyword_list in keyword_lists:
        list_pattern = '|'.join(re.escape(preprocess_text(keyword)) for keyword in keyword_list)
        pattern_parts.append(f'({list_pattern})')
    
    combined_pattern = '|'.join(pattern_parts)
    return combined_pattern

def filter_comments(text, categories):
    """Filter and extract full comments based on categories."""
    lines = text.split('\n')
    filtered_comments = []
    
    # Preprocess categories
    processed_categories = [preprocess_text(' '.join(category)) for category in categories]
    
    comment_start = None
    current_comment = []
    
    for line in lines:
        preprocessed_line = preprocess_text(line)
        
        if any(category in preprocessed_line for category in processed_categories):
            if current_comment:
                filtered_comments.append('\n'.join(current_comment))
                current_comment = []
            current_comment.append(line)
        else:
            if current_comment:
                current_comment.append(line)
                # Consider end of comment if next line is empty or if there's a section break
                if not preprocessed_line:
                    filtered_comments.append('\n'.join(current_comment))
                    current_comment = []
    
    if current_comment:
        filtered_comments.append('\n'.join(current_comment))
    
    return filtered_comments

# Loop through all pages and extract text
for page_number, page in enumerate(pages, start=1):
    # Extract text from the current page
    page_text = pytesseract.image_to_string(page)
    # Clean the text by removing unwanted content
    cleaned_text = clean_text(page_text)
    full_text += f"\n\n--- Page {page_number} ---\n\n"
    # Append the cleaned text from the page to the full text
    full_text += cleaned_text

# Extract section 143(3)
section_143_text = extract_section(full_text, "Section 143 (3)")

# Define categories to match
categories = [
    ["information", "explanation", "sought", "obtain"],
    ["proper", "books", "accounts"],
    ["branch"],
    ["financial statement", "agreement"],
    ["accounting standard", "as"],
    ["observations", "comments"],
    ["directors", "164(2)"],
    ["qualification", "reservations", "adverse", "remarks"],
    ["internal", "financial", "control", "systems"],
    ["pending", "litigations"],
    ["long-term contracts", "derivative contract"],
    ["investor", "education", "protection fund"],
    ["dividend"],
    ["audit trail"]
]

# Filter and extract comments based on categories
filtered_comments = filter_comments(section_143_text, categories)

with open("file.txt", "w") as output:
    output.writelines(filtered_comments)