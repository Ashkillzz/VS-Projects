import json
import re

def extract_data(text):
    data = {}

    # Key-Value Pairs
    kv_pairs = {}
    kv_pattern = r"Key: (.+?), Value: (.+)"
    for match in re.finditer(kv_pattern, text):
        key = match.group(1).strip()
        value = match.group(2).strip()
        kv_pairs[key] = value
    data["key_value_pairs"] = kv_pairs

    # Tables
    tables = []
    table_pattern = r"Table with (\d+) cells:(.*?)(?=(Table with|$))"  # Lookahead assertion
    for table_match in re.finditer(table_pattern, text, re.DOTALL):
        num_cells = int(table_match.group(1))
        table_content = table_match.group(2)

        rows = []
        cell_pattern = r"- Cell \((\d+), (\d+)\): (.*)"
        cell_matches = list(re.finditer(cell_pattern, table_content))

        # Determine number of rows based on cell indices
        max_row = 0
        for cm in cell_matches:
          max_row = max(max_row, int(cm.group(1)))
        
        for r in range(max_row + 1):
          row = []
          for c in range(10): # Assume max 10 columns for now - adjust as needed
            cell_value = None
            for cm in cell_matches:
                if int(cm.group(1)) == r and int(cm.group(2)) == c:
                    cell_value = cm.group(3).strip()
                    break  # Stop searching once cell is found
            row.append(cell_value)
          rows.append(row)
        tables.append(rows)
    data["tables"] = tables
    return data


if __name__ == '__main__':
   
    extracted_text = ""
    json_file = r'D:\Aswin\VS Projects\AzuretoJSON.json'

    input_file = r'D:\Aswin\VS Projects\ocr_result.txt'

    # Read the contents of the input file
    with open(input_file, "r", encoding="utf-8") as f:
        extracted_text = f.read()


    with open(input_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    dt = extract_data(extracted_text)

    with open(json_file, 'w') as file:
        json.dump(dt, file, indent=4)