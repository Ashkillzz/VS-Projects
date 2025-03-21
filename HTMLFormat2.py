import json
from bs4 import BeautifulSoup

def extract_keys_from_json(json_file, keys_dict, output_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    extracted_data = {keys_dict["name"]: []}
    
    # Extract keys from dictionary and use abbreviations as keys
    for key, abbreviation in keys_dict.get("keys", {}).items():
        if key in json_data:
            extracted_data[keys_dict["name"]].append({abbreviation: str(json_data[key])})
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=4)

def format_html_text(json_file, html_keys_dict, output_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    formatted_data = {html_keys_dict["name"]: []}
    
    for key, abbreviation in html_keys_dict.get("keys", {}).items():
        if key in json_data and isinstance(json_data[key], str):
            soup = BeautifulSoup(json_data[key], "html.parser")
            formatted_data[html_keys_dict["name"]].append({abbreviation: soup.prettify()})
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=4)

# Example usage
keys_dict = {
    "name": "XML_Fields",
    "keys": {
        "DisclosureInAuditorsReportRelatingToFixedAssets": "AudRep",
        "WhetherCompaniesAuditorsReportOrderIsApplicableOnCompany": "CARO",
        "CompletePostalAddressOfPlaceOfMaintenanceOfComputerServersStoringAccountingData" : "CompServ"
    }
}
html_keys_dict = {
    "name": "html_data",
    "keys": {
        "DisclosureInAuditorsReportExplanatoryTextBlock": "DisAudRepExp",
        "DisclosureInBoardOfDirectorsReportExplanatoryTextBlock" : "DisBODRepExp"
    }
}

extract_keys_from_json("XBRL_202324.json", keys_dict, "extracted_data.json")
format_html_text("XBRL_202324.json", html_keys_dict, "formatted_html.json")
