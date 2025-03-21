import xmltodict
import json

# Load XML File
xml_file = "D:\Aswin\VS Projects\AOC-4 XBRL\Tookitaki\Tookitaki.xml"
json_output_file = "XBRL_202324.json"

with open(xml_file, "r", encoding="utf-8") as file:
    xml_content = file.read()

# Convert XML to Dictionary
xml_dict = xmltodict.parse(xml_content)

# Convert Dictionary to JSON
json_data = json.dumps(xml_dict, indent=4)

# Save to a JSON File
with open(json_output_file, "w", encoding="utf-8") as json_file:
    json_file.write(json_data)

print(f"JSON file saved as {json_output_file}")


