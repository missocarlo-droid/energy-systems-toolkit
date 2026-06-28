import pandas as pd
from cleaning import cleaning_csv
import os
from docxtpl import DocxTemplate
from datetime import date
from update_input import update_csv
import pdb


# Create folder to store the output PDFs created
output_folder = 'Word_filled_contracts'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
# Input word template
word_template = "END_USER_CONTRACT.docx"
# Input CSV (REGISTRATION form)
#input_xlsx = "WFP.xlsx"
#
#dfa = pd.read_excel(input_xlsx)
#dfa.to_csv("WFP.csv", index=False)
input_csv = "data.csv"
dfx = update_csv(input_csv)
df = cleaning_csv(dfx)
#print(df.head())
#df.to_csv("cleaned_data.csv", index=False)
# Hardcoded values for fields not present in the CSV (based on previous documents/defaults)
default_stove_type = "JIKO RAFIKI"
default_date = date.today().strftime("%d/%m/%Y") # Uses today's date (DD/MM/YYYY)
default_secondary_phone = "-" 
try:
    # 1. Load the template and data
    doc = DocxTemplate(word_template)
    data = df
    print(f"Loaded {len(data)+1} client records from {input_csv}.")
    print("Generating documents...")
    # 2. Loop through each row in the data
    for index, row in data.iterrows():
        # --- Prepare Data Context ---
        # Combine First and Last Name
        full_name = f"{row['client.firstName']} {row['client.lastName']}"
        id_client = row['client.clientNumber']
        # Combine Address fields (Village, Hamlet, Address)
        # We use the Village and Address columns for the full location
        full_address = f"{row['County']}, {row['Village']}, {row['Neighbour']}"
        mobile_number = row['Mobile']
        # Since Stove ID is not in the registration CSV 
        # For this script, we use a placeholder that you must manually update in the output file.
        stove_id_placeholder = "KIG"
        context = {
            'FULL_NAME': full_name,
            'ID_CLIENT': id_client,
            #'FULL_ADDRESS': full_address,
            'VILLAGE': row['Village'],
            'HAMLET': row['Neighbour'],
            'PHONE_PRIMARY': mobile_number,
            # Hardcoded/Default Fields
            'PHONE_SECONDARY': default_secondary_phone,
            'STOVE_TYPE': default_stove_type,
            'DATE_RECEIVED': "/2026", #default_date,
            'STOVE_ID': stove_id_placeholder
        }
        # 3. Render and Save the document
        doc.render(context)
        # Define the output file name using the client's name and ID
        output_filename = os.path.join(
            output_folder,
            f"{full_name.replace(' ', '_')}_{row['client.clientNumber']}.docx"
        )
        doc.save(output_filename)
        print(f"  -> Generated: {output_filename}")
    print("\n✅ All documents generated successfully in the 'Filled_Contracts' folder!")
except FileNotFoundError as e:
    print(f"\n❌ Error: The script could not find a file. Check the names: {e}")
except KeyError as e:
    print(f"\n❌ Error: Missing column in CSV. Check if the column name matches the key: {e}")
except Exception as e:
    print(f"\n❌ An unexpected error occurred: {e}")

