import json
import os


key_path = "/home/ayush/Desktop/angelone_smartapi/angelOne"
os.chdir(key_path)
# Read data from the JSON file
tokens_to_check = []

# Open and read the JSON file
with open('output.json', 'r') as json_file:
    json_data = json.load(json_file)

# Append JSON data to tokens_to_check array
for item in json_data:
    token_symbol_dict = {"token": item["token"], "symbol": item["symbol"]}
    tokens_to_check.append(token_symbol_dict)

# Printing tokens_to_check after appending JSON data
print(tokens_to_check)