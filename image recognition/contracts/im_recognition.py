import os
import glob
import pandas as pd
import requests
import datetime
import pdb
import json
import time
import re
from gpt_run import gpt_classify_image
from cleaning import cleaning_csv

assignment_df = 'assignment.csv' # ASSIGNMENT form
client_df = 'clients.csv'  # CLIENTS form

clean_df = cleaning_csv(assignment_df, client_df)
clean_df.to_csv("cleaned_data.csv", index=False) # Not strictly necessary


api_key = os.getenv("CONTRACT_OPENAI_API_KEY") # keys: GEMINI_API_KEY & GEMINI_API_KEY_ANDRE & CONTRACT_OPENAI_API_KEY
if not api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY not found in environment variables.")


timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filenameOutput = f"final_output_{timestamp}.csv"

# Create directories to save the images
image_dir_stove = 'downloaded_images_contract'
if not os.path.exists(image_dir_stove):
    os.makedirs(image_dir_stove)

files = glob.glob("intermediate_output_*.csv")

if not files:
    raise FileNotFoundError("No intermediate_output_*.csv files found in working directory.")

# Option 1: pick by modification time (safest)
latest_file = max(files, key=os.path.getmtime)

# Option 2: pick by filename order (works since timestamp is YYYYMMDD_HHMMSS)
# latest_file = sorted(files)[-1]

print(f"Reading from latest file: {latest_file}")
#Read only the first 10 rows for testing
df = pd.read_csv(latest_file)

# Authentication details
username = "username"  # Replace with your actual username
password = "password"  # Replace with your actual password
# API endpoint for signed urls
url = "https://data.upya.io/data/forms/signedUrls"

status = ["IDNotFoundInCSV", "NoValidURLGenerated", "NoCorrectDownolad", "CheckNotPassed", "Approved"]


for index, row in df.iterrows():
    time.sleep(1) # To avoid hitting the server too quickly

    if index % 1 == 0:
        d = {}

        ContractCheckStatus = 0

        #read from input (intermediate_output.csv)
        ClientID = row['ClientID']

        ContractID = row['ContractPic'] # Must be ContractPic!!!! but to try also PicNIDA, PicStove, PicStove2, PicStove3
        AgentName = row['AgentName']
        CookstoveType = row['CookstoveType']

        ContractPic2 = row['ContractPic2']  # New field to check for extra contract picture

        contract_image_path = None

        d['ClientID'] = ClientID
        d['AgentName'] = AgentName
        d['CookstoveType'] = CookstoveType

        d['StoveNumber'] = ''
        d['SigningDate'] = ''

        d['ContractCheckStatus'] = ''

        # New column: error message if ContractPic2 is not "Not Available"
        if isinstance(ContractPic2, str) and ContractPic2.strip().lower() != 'not available':
            d['DoubleContractCheck'] = 'Double Contract'
        else:
            d['DoubleContractCheck'] = 'Ok'

        d['ClientNumberCheck'] = 'Ok'

        #check if read from .csv was succesful              
        if ContractID == "Not Available":
            d['ContractCheckStatus'] = status[ContractCheckStatus]
            print(f"ContractID not available for ClientID {ClientID}")
            ContractCheckStatus = -1

        # Check Contract
        if ContractCheckStatus != -1:
            ContractCheckStatus += 1
            try:
                #get the URL
                payload = {
                    "listOfIds": ContractID,
                    "useS3": True
                }
                response = requests.request("POST", url, json=payload, auth=(username, password))
                data = json.loads(response.text)

                if isinstance(data, list) and len(data) > 0 and 'URL' in data[0]:

                    ContractURL = data[0]['URL']

                    ContractCheckStatus += 1
                    # Download the image
                    try:
                        # Download the image
                        response = requests.get(ContractURL, stream=True)
                        response.raise_for_status() # Raise an exception for bad status codes

                        # Determine the file path
                        contract_image_filename = f"{ClientID}_contract.jpg"
                        contract_image_path = os.path.join(image_dir_stove, contract_image_filename)

                        # Save the image
                        with open(contract_image_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        ContractCheckStatus += 1

                        # Classify the image using the model
                        # Build expected_values vector by looking up the client's row in cleaned_data.csv 
                        try:
                            data_df = clean_df
                            #data_df = pd.read_csv('cleaned_data.csv', dtype=str) # Could be data_df = clean_df if we want to avoid re-reading
                        except Exception as e:
                            print(f"Could not read data.csv: {e}")
                            data_df = None

                        expected_values = []
                        if data_df is not None:
                            # Normalize column name (there is a header 'client.clientNumber')
                            key_col = None
                            for col in data_df.columns:
                                if col.strip().lower() == 'client.clientnumber':
                                    key_col = col
                                    break
                            if key_col is None:
                                # try alternative
                                key_col = 'client.clientNumber' if 'client.clientNumber' in data_df.columns else data_df.columns[0]

                            match_rows = data_df[data_df[key_col] == str(ClientID)]
                            if not match_rows.empty:
                                client_row = match_rows.iloc[0]
                                # Select fields to include in expected_values. Map to what gemini prompt expects.
                                expected_values = {
                                    #'FullName': client_row.get('client.firstName', '') + ' ' + client_row.get('client.lastName', client_row.get('client.lastName', '')) if client_row is not None else '',
                                    #'FullAdress': ', '.join(filter(None, [client_row.get('Ward', ''), client_row.get('Village', ''), client_row.get('Hamlet', ''), client_row.get('Adress', '')])),
                                    #'Phone': client_row.get('Mobile', client_row.get('Mobile', '')),
                                    #'StoveType': client_row.get('Product', ''),
                                    'Date': client_row.get('signingDate', ''),
                                    'StoveNumber': client_row.get('Scan', '') if 'Scan' in client_row.index else '',
                                    'ClientNumber': client_row.get(key_col, '')
                                }
                                print(f"Expected values for ClientID {ClientID}: {expected_values}")
                            else:
                                print(f"No matching row found in data.csv for ClientID {ClientID}")
                            
                        d['StoveNumber'] = expected_values.get('StoveNumber', '')
                        d['SigningDate'] = expected_values.get('Date', '')

                        try:
                            predicted_class, choice, gpt_check = gpt_classify_image(contract_image_path, api_key, expected_values=expected_values)
                            print(f"Client {ClientID} - Contract Predicted class: {predicted_class}")
                        
                        except Exception as e:
                            print(f"GPT classification failed for ClientID {ClientID}: {e}")
                            predicted_class = ""  # Default to "Unreadable"
                            gpt_check = "Unreadable"

                        # Compare predicted class with expected type (CookstoveType)
                        if gpt_check == "Approved":
                            ContractCheckStatus += 1

                        d['ContractCheckStatus'] = status[ContractCheckStatus]

                        if not re.fullmatch(r"[1-3]", predicted_class.strip()):
                            d['ClientNumberCheck'] = predicted_class # In case ClientNumber is wrong"

                    except requests.exceptions.RequestException as e:
                        d['ContractCheckStatus'] = status[ContractCheckStatus] 
                        print(f"ContractURL download failed for ClientID {ClientID}: {e}")

                else:
                    d['ContractCheckStatus'] = status[ContractCheckStatus]
                    print(f"No valid data returned for ClientID {ClientID}: {data}")


            except requests.exceptions.RequestException as e:
                    d['ContractCheckStatus'] = status[ContractCheckStatus] 
                    print(f"ContractURL request failed for ClientID {ClientID}: {e}")

        #Delete downloaded images to save space
        if contract_image_path and os.path.exists(contract_image_path):
            os.remove(contract_image_path)
    else:
        continue
    
    df_output = pd.DataFrame([d])
    df_output.to_csv(filenameOutput, mode='a', header=not pd.io.common.file_exists(filenameOutput), index=False)