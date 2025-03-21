from xfa import Xfa
import json

xfa = Xfa("D:\Aswin\VS Projects\AOC Forms\[05-11-2022]_Form_AOC-4-05112022_signed_3.pdf")
output: str = xfa.convert(output = "json")

with open("json_file", 'w') as file:
    json.dump(output, file, indent=4)