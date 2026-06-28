import requests
import json
import pandas as pd
import datetime
import os
import time

# Get current timestamp for filename
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"intermediate_output_{timestamp}.csv"

# Authentication details
username = "missocarlo@outlook.com"
password = "1234567!"

url = "https://data.upya.io/data/search/forms"

with open("ids.txt", "r") as f:
    id_list = [line.strip() for line in f]

print(len(id_list))
# run only for the first 10 ids for testing
for id in id_list:
    time.sleep(1)  # To avoid hitting the server too quickly


    payload = {
        "query": {
            "clientNumber": id,
        }
    }

    response = requests.post(url, json=payload, auth=(username, password))
    response_json = json.loads(response.text)

    data = json.loads(response.text)[1]['creditItems']


    acceptable_codes = ['ContractPic'] # Must be ContractPic

    #AllKys = ['ContractPic', 'PicNIDA', 'DocPic', 'PicStove', 'CookstoveType', 'DocumentOrNationalNumber']

    d = {}
    d['ClientID'] = id

    for element in data:
        if element['code'] in acceptable_codes and element['isPicture'] == True:
            d[element['code']] = element['_id']
        elif element['code'] == 'CookstoveType':
            d[element['code']] = element['translatedAnswer']
        elif element ['code'] == 'NationalIdentificationNumber' or element ['code'] == 'DocumentNumber':
            d['DocumentOrNationalNumber'] = element['answer']
        agent_profile = response_json[1]['agent']['profile']
        d['AgentName'] = f"{agent_profile.get('firstName', '')} {agent_profile.get('lastName', '')}".strip()
    

    for k in acceptable_codes:
        if not k in d:
            d[k] = "Not Available"

    # Extract _id from data2 if available
    if len(response_json) > 2 and isinstance(response_json[2], dict):
        data2 = json.loads(response.text)[2]['creditItems']
        d['ContractPic2'] = "Not Available"
        if isinstance(data2, list):
            for element in data2:
                if element.get("isPicture") is True:
                    d['ContractPic2'] = element["_id"]
                    break
    else:
        data2 = []  # behaves as "doesn't exist"

    print("_"*50)

    for k, v in d.items():
        print(f"{k}: {v}")  

    #save in "intermediate_output.csv" file the dictionary d for each id
    #columns = ['ClientID', 'DocumentOrNationalNumber', 'DocPic', 'PicNIDA', 'CookstoveType', 'PicStove']
    required_columns = ["ClientID", "CookstoveType", "ContractPic", "AgentName","ContractPic2"]
    for col in required_columns:
        if col not in d:
            d[col] = "Not Available"

    df = pd.DataFrame([d])

    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)