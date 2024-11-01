import requests
import json
import csv
import math

API = 'https://www.footballtransfers.com/us/transfers/actions/confirmed/overview'
JSON_DEST = 'data/transfers.json'
CSV_DEST = 'data/transfers.csv'
MAX_ITEMS_PER_REQ = 4848
MAX_ITEMS = 13353
SEASON_ID = 5847 # 2023 - 2024

data = []

for page in range(1, math.ceil(MAX_ITEMS / MAX_ITEMS_PER_REQ) + 1):
    body = {
        "season": 5847,
        "page": page,
        "pageItems": MAX_ITEMS_PER_REQ
    }

    response = requests.post(API, data=body)
    print(response)

    rawData = json.loads(response.text)
    for record in rawData['records']:
        data.append({
            "player_id": record['player_id'],
            "player_name": record['player_name'],
            "country_name": record['country_name'],
            "age": record['age'],
            "position_name": record['position_name'],
            "club_from_name": record['club_from_name'],
            "club_to_name": record['club_to_name'],
            "amount": record['amount'],
            "date_transfer": record['date_transfer']
        })

print(len(data))

with open(JSON_DEST, mode='w', encoding='utf-8') as jsonFile:
    json.dump(data, jsonFile, ensure_ascii=False, indent=4)

with open(CSV_DEST, mode='w', newline='', encoding='utf-8') as csvFile:
    fieldnames = data[0].keys()
    writer = csv.DictWriter(csvFile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

