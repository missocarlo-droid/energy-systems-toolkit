import pandas as pd
import requests
import json
import datetime
import pdb
import os
import time
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"intermediate_output_{timestamp}.csv"

# Method 1: Read lines and strip newlines
with open("ids.txt", "r") as f:
    id_list = [line.strip() for line in f]

print(len(id_list))


username = "missocarlo@outlook.com"
password = "1234567!"
# Step 1: GET request for authentication (optional, can be skipped if you just want to do the POST)
# This step is good for confirming authentication works before moving on.


url = "https://data.upya.io/data/search/forms"

for id in id_list:
    time.sleep(1)  # Sleep for 1 second between requests to avoid overwhelming the server

    payload = {
        "query": {
            "clientNumber": id,
        }
    }

    response = requests.post(url, json=payload, auth=(username, password))

    data = json.loads(response.text)[0]['creditItems']

    acceptable_codes = ['DocPic', 'PicNIDA', 'PicStove']

    AllKys = ['DocPic', 'PicNIDA', 'PicStove', 'CookstoveType', 'DocumentOrNationalNumber']

    d = {}
    d['ClientID'] = id

    for element in data:
        if element['code'] in acceptable_codes and element['isPicture'] == True:
            d[element['code']] = element['_id']
        elif element['code'] == 'CookstoveType':
            d[element['code']] = element['translatedAnswer']
        elif element ['code'] == 'NationalIdentificationNumber' or element ['code'] == 'DocumentNumber':
            d['DocumentOrNationalNumber'] = element['answer']
             
            if not any(char.isdigit() for char in d['DocumentOrNationalNumber']):
                d['DocumentOrNationalNumber'] = "Not Available"

    for k in AllKys:
        if not k in d:
            d[k] = "Not Available"

    print("_"*50)

    for k, v in d.items():
        print(f"{k}: {v}")  

    #save in "intermediate_output.csv" file the dictionary d for each id
    columns = ['ClientID', 'DocumentOrNationalNumber', 'DocPic', 'PicNIDA', 'CookstoveType', 'PicStove']
    df = pd.DataFrame([d], columns=columns)

    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)














