import google.generativeai as genai  # Google Gemini SDK
import json
import os
import re

# Configure Gemini API (Use Environment Variable if possible)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")  
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

genai.configure(api_key=GEMINI_API_KEY, transport="rest")  # Using REST

def extract_json_from_llm_response(llm_output):
    """Extracts JSON from LLM response."""
    try:
        return json.loads(llm_output)  # Direct JSON parsing
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", llm_output, re.DOTALL)  # Extract JSON block
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass  
        return None  

def gemini_generate_json(ocr_text):
    """Takes OCR text and returns structured JSON using Gemini Pro."""
    try:
        model = genai.GenerativeModel("gemini-pro")  # Load Gemini Pro
        prompt = f"""
        Analyze the below given OCR text and extract structured information in JSON format. The OCR text data contains a mix of paragraphs and table data, so accordingly provide me the JSON output adhering to the content format.

        OCR Text:
        {ocr_text}

        
        ----End of OCR Generated Text----
        """

        response = model.generate_content(prompt)  # Get response
        print("RAW RESPONSE:", response)  # Debugging output

        if response and response.text:
            json_output = extract_json_from_llm_response(response.text)
            return json_output if json_output else "Failed to extract JSON."
        else:
            return "Unexpected response format from Gemini API."
    
    except Exception as e:
        return f"An error occurred: {e}"

# Read OCR text from a .txt file
def read_ocr_text(file_path):
    """Reads text content from a .txt file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read().strip()  # Read and remove extra spaces
    except FileNotFoundError:
        return "Error: OCR text file not found."
    except Exception as e:
        return f"Error reading OCR text file: {e}"

# Example Usage
if __name__ == "__main__":
    txt_file = "D:\Aswin\VS Projects\Files\Text Files\LLMWhispererOutput.txt"  # Replace with your actual OCR text file path

    ocr_text = read_ocr_text(txt_file)  # Read OCR text from file

    if ocr_text.startswith("Error:"):  # Handle file read errors
        print(ocr_text)
    else:
        json_data = gemini_generate_json(ocr_text)

        if isinstance(json_data, dict):
            print(json.dumps(json_data, indent=4))  # Pretty print JSON
            with open("D:\Aswin\VS Projects\Files\JSON FIles\Gemini_LLMWhisper.json", "w") as f:
                json.dump(json_data, f, indent=4)
        else:
            print(json_data)  # Print error message if JSON extraction fails
