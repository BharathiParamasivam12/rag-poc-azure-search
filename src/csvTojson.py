import csv
import json
import os

def csv_to_json(csv_file_path, json_file_path):
    data = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    
    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)
    
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

csv_to_json('/Users/manop/Desktop/Rag-azure-search/rag-poc-azure-search/data/raw/Datafiniti_Hotel_Reviews.csv',
            '/Users/manop/Desktop/Rag-azure-search/rag-poc-azure-search/data/transformed/Datafiniti_output.json')