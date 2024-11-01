import json
import csv
from collections import OrderedDict

def flatten(d, parent_key = ''):
    items = OrderedDict()
    for key, value in d.items():
        new_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            items.update(flatten(value, new_key))
        else:
            items[new_key] = value
    return items

print('reading json')
with open('data/players.json', 'r', encoding='utf-8') as jsonFile:
    data = json.load(jsonFile)

data = [flatten(item) for item in data]

with open('data/results.csv', mode='w', newline='', encoding='utf-8') as destination:
    fieldNames = data[0].keys()
    
    writer = csv.DictWriter(destination, fieldnames=fieldNames)
    
    writer.writeheader()
    
    writer.writerows(data)
    
    print(f'written {len(fieldNames)} fields and {len(data)} records')

