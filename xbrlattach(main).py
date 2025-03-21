import json

# Load the JSON file
file_path = "D:\Aswin\VS Projects\XBRL_202324.json"
with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Define the object names to extract
object_names = [
    "RevenueFromSaleOfProducts",
    "RevenueFromSaleOfServices",
    "RevenueFromOperationsOtherThanFinanceCompany",
    "RevenueFromOperations",
    "Revenue"
]

# Extract relevant data
xbrl_data = data.get("xbrli:xbrl", {})

# Find and collect matching elements
extracted_data = {}
for key in xbrl_data.keys():
    for obj_name in object_names:
        if obj_name.lower() in key.lower():
            extracted_data[key] = xbrl_data[key]

# Display the extracted results
print(json.dumps(extracted_data, indent=4))
