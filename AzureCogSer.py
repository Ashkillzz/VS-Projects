import json
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# Azure Form Recognizer credentials
AZURE_FORM_RECOGNIZER_ENDPOINT = "https://data-verification.cognitiveservices.azure.com/"  # Replace with your endpoint
AZURE_FORM_RECOGNIZER_KEY = ""  # Replace with your API key

# Initialize DocumentAnalysisClient
document_analysis_client = DocumentAnalysisClient(
    endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
)

def analyze_document(file_path: str, model_id: str = "prebuilt-document"):
    """
    Analyze a PDF document using Azure Form Recognizer and return JSON results.

    Args:
        file_path (str): Path to the PDF document.
        model_id (str): ID of the model to use. Default is "prebuilt-document".

    Returns:
        dict: JSON output of the analyzed document.
    """
    with open(file_path, "rb") as document:
        poller = document_analysis_client.begin_analyze_document(
            model_id=model_id,
            document=document
        )
        result = poller.result()
        return result

def process_analysis_result(result, output_text_file):
    """
    Process and save key insights from the Azure Form Recognizer result into a text file.

    Args:
        result: The analyzed document result.
        output_text_file (str): Path to the output text file.
    """
    with open(output_text_file, "w", encoding="utf-8") as file:
        file.write("\n---- Document Analysis Results ----\n")
        for page in result.pages:
            file.write(f"Page number: {page.page_number}\n")
            file.write(f"Width: {page.width}, Height: {page.height}, Unit: {page.unit}\n")

        file.write("\n---- Extracted Key-Value Pairs ----\n")
        for kv_pair in result.key_value_pairs:
            if kv_pair.key and kv_pair.value:
                file.write(f"Key: {kv_pair.key.content}, Value: {kv_pair.value.content}\n")

        file.write("\n---- Extracted Tables ----\n")
        for table in result.tables:
            file.write(f"Table with {len(table.cells)} cells:\n")
            for cell in table.cells:
                file.write(f" - Cell ({cell.row_index}, {cell.column_index}): {cell.content}\n")

        file.write("\n---- Extracted Lines ----\n")
        for line in result.lines:
            file.write(f"Line: {line.content}\n")

if __name__ == "__main__":
    pdf_path = "D:\Aswin\VS Projects\Files\PDF Files\StandaloneFS(BS_PL).pdf"  # Replace with the path to your PDF
    text_output_path = "Files\Text Files\ocr_result.txt"  # Output text file
    try:
        # Analyze the document
        analysis_result = analyze_document(pdf_path)
        
        # Process and save results
        process_analysis_result(analysis_result, text_output_path)
        
        print(f"Results saved to {text_output_path}")
    except Exception as e:
        print(f"Error: {e}")
