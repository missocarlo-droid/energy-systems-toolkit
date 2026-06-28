import pandas as pd
import requests
#import torch
import os
import glob
import pdb
import json
import datetime
import time
#from model_run import clip_classify_image
from id_run import id_classify_image
from stove_run import stove_classify_image
from transformers import AutoProcessor, AutoModelForZeroShotImageClassification


api_key = os.getenv("STOVE_OPENAI_API_KEY") # API keys: GEMINI_API_KEY || STOVE_OPENAI_API_KEY
if not api_key:
    raise EnvironmentError("❌ STOVE_OPENAI_API_KEY_ANDRE not found in environment variables.")

""" CLIP
#load models
processor = AutoProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = AutoModelForZeroShotImageClassification.from_pretrained("openai/clip-vit-base-patch32")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


# Prompt testuali per ogni classe
prompts_ID = {
        "ID": [
        "a light orange national identity card with a portrait photo and a QR code and a barcode",
    "a light blue official ID card with a portrait photo and signature",
    "a blurry government-issued identity document",
    "a personal identification card on a table",
    "a personal identification card on a wooden surface"
    "a close-up photo of an identity card with a face photo",
    "a handwritten number on a piece of paper"
    ],

    "other": [
        "a selfie of a person",
    "a photo of a random object like a phone",
    "a close-up of a face without any card",
    "a landscape photo without documents",
    "a picture of food",
    "an illegible identity card"
    ],
        "Contract": [
            "a printed contract without any photo",
            "a paper with written text but no ID photo"
        ]
}
"""


# Create a timestamped filename for output
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
filenameOutput = f"final_output_{timestamp}.csv"

# Create directories to save the images
image_dir_stove = 'downloaded_images_stove'
if not os.path.exists(image_dir_stove):
    os.makedirs(image_dir_stove)

image_dir_nida = 'downloaded_images_nida'
if not os.path.exists(image_dir_nida):
    os.makedirs(image_dir_nida)

files = glob.glob("intermediate_output_*.csv")

if not files:
    raise FileNotFoundError("No intermediate_output_*.csv files found in working directory.")

# Option 1: pick by modification time (safest)
latest_file = max(files, key=os.path.getmtime)

# Option 2: pick by filename order (works since timestamp is YYYYMMDD_HHMMSS)
# latest_file = sorted(files)[-1]

print(f"Reading from latest file: {latest_file}")
df = pd.read_csv(latest_file)


username = "username" #replace with your actual username
password = "password" #replace with your actual password

url = "https://data.upya.io/data/forms/signedUrls"

status = ["IDNotFoundInCSV", "NoValidURLGenerated", "NoCorrectDownolad", "CheckNotPassed", "Approved"]
#
for index, row in df.iterrows():
    time.sleep(1)  # Sleep for 1 second between requests to avoid overwhelming the server
    
    if index % 1 == 0:
          
        d = {}

        DocCheckStatus = 0
        StoveCheckStatus = 0

        #read from input (intermediate_output.csv)
        ClientID = row['ClientID']

        # DocID must be equal to DocPic if PicNIDA is not available and viceversa
        DocID = row['PicNIDA']
        if DocID == "Not Available":
            DocID = row['DocPic']

        StoveID = row['PicStove']
        DocumentOrNationalNumber = row['DocumentOrNationalNumber']
        CookstoveType = row['CookstoveType']

        doc_image_path = None
        stove_image_path = None

        d['ClientID'] = ClientID
        d['CookstoveType'] = CookstoveType
        d['DocumentOrNationalNumber'] = DocumentOrNationalNumber
        d['DocCheckStatus'] = status[DocCheckStatus]


        #check if read from .csv was succesful
        if DocumentOrNationalNumber == "Not Available":
            DocCheckStatus = 4 #Approved
            d['DocCheckStatus'] = status[DocCheckStatus]
        else:
            if DocID == "Not Available":
                d['DocCheckStatus'] = status[DocCheckStatus]
                DocCheckStatus = -1


        if StoveID == "Not Available":
            d['StoveCheckStatus'] = status[StoveCheckStatus]
            StoveCheckStatus = -1

            
        # ID
        if DocCheckStatus != -1 and DocCheckStatus != 4:
            DocCheckStatus += 1
            try:
                #get the URL
                payload = {
                    "listOfIds": DocID,
                    "useS3": True
                }
                response = requests.request("POST", url, json=payload, auth=(username, password))
                data = json.loads(response.text)

                if isinstance(data, list) and len(data) > 0 and 'URL' in data[0]:

                    DocURL = data[0]['URL']

                    DocCheckStatus += 1
                    # Download the image
                    try:
                        # Download the image
                        response = requests.get(DocURL, stream=True)
                        response.raise_for_status() # Raise an exception for bad status codes

                        # Determine the file path
                        doc_image_filename = f"{ClientID}_stove.jpg"
                        doc_image_path = os.path.join(image_dir_nida, doc_image_filename)

                        # Save the image
                        with open(doc_image_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        DocCheckStatus += 1

                        # Classify the image using the model
                        #predicted_class, class_scores, results = clip_classify_image(doc_image_path, device, processor, model, prompts_ID) # -- CLIP
                        predicted_class = id_classify_image(doc_image_path, api_key)

                        print(f"Client {ClientID} - NIDA Predicted class: {predicted_class}")
                        #print(f"NIDA Class scores: {class_scores}")  # -- CLIP

                        # Compare predicted class with expected type ("ID")
                        if predicted_class == "ID":
                            DocCheckStatus += 1

                        d['DocCheckStatus'] = status[DocCheckStatus]

                    except requests.exceptions.RequestException as e:
                        d['DocCheckStatus'] = status[DocCheckStatus] 
                        print(f"DocURL download failed for ClientID {ClientID}: {e}")

                else:
                    d['DocCheckStatus'] = status[DocCheckStatus]
                    print(f"No valid data returned for ClientID {ClientID}: {data}")



            except requests.exceptions.RequestException as e:
                if DocumentOrNationalNumber == "Not Available":
                    DocCheckStatus = 4 #Approved
                    d['DocCheckStatus'] = status[DocCheckStatus]
                else:
                    d['DocCheckStatus'] = status[DocCheckStatus] 
                    print(f"DocURL request failed for ClientID {ClientID}: {e}")
           

        # Stove
        if StoveCheckStatus != -1:
            StoveCheckStatus += 1
            try:
                #get the URL
                payload = {
                    "listOfIds": StoveID,
                    "useS3": True
                }
                response = requests.request("POST", url, json=payload, auth=(username, password))
                data = json.loads(response.text)

                if isinstance(data, list) and len(data) > 0 and 'URL' in data[0]:
                    
                    StoveURL = data[0]['URL']

                    StoveCheckStatus += 1
                    # Download the image
                    try:
                        # Download the image
                        response = requests.get(StoveURL, stream=True)
                        response.raise_for_status() # Raise an exception for bad status codes

                        # Determine the file path
                        stove_image_filename = f"{ClientID}_stove.jpg"
                        stove_image_path = os.path.join(image_dir_stove, stove_image_filename)

                        # Save the image
                        with open(stove_image_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        StoveCheckStatus += 1

                        # Mettere virgolette
                        # Classify the image using the model
                        predicted_class = stove_classify_image(stove_image_path, api_key)
                        #predicted_class = gemini_classify_image(stove_image_path, api_key) -- GEMINI

                        print(f"Client {ClientID} - Stove Predicted class: {predicted_class}")
                        #print(f"Stove Explanation: {expl}")
                        # Compare predicted class with expected type (CookstoveType)
                        if predicted_class == CookstoveType:
                            StoveCheckStatus += 1
                        # Mettere virgolette

                        d['StoveCheckStatus'] = status[StoveCheckStatus]

                    except requests.exceptions.RequestException as e:
                        d['StoveCheckStatus'] = status[StoveCheckStatus] 
                        print(f"StoveURL download failed for ClientID {ClientID}: {e}")

                else:
                    d['StoveCheckStatus'] = status[StoveCheckStatus]
                    print(f"No valid data returned for ClientID {ClientID}: {data}")

            except requests.exceptions.RequestException as e:
                    d['StoveCheckStatus'] = status[StoveCheckStatus] 
                    print(f"StoveURL request failed for ClientID {ClientID}: {e}")


        # Delete downloaded images to save space
        if doc_image_path and os.path.exists(doc_image_path):
            os.remove(doc_image_path)
        if stove_image_path and os.path.exists(stove_image_path):
            os.remove(stove_image_path)

    else:
        continue

    # Save results to output CSV
    df_output = pd.DataFrame([d])
    df_output.to_csv(filenameOutput, mode='a', header=not pd.io.common.file_exists(filenameOutput), index=False)