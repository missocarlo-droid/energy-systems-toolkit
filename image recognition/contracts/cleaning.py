import pandas as pd

def cleaning_csv(assignment_file, client_file):
    # Read the files
    df = pd.read_csv(assignment_file, low_memory=False)
    df2 = pd.read_csv(client_file)

    # Strip whitespace and potential BOM from column names
    df.columns = df.columns.str.replace('\ufeff', '', regex=False)
    df.columns = df.columns.str.replace('?', '', regex=False)
    df2.columns = df2.columns.str.replace('\ufeff', '', regex=False)
    df2.columns = df2.columns.str.replace('?', '', regex=False)


    cols_to_drop = [
    'client.status', 'collector.profile.lastName', 'collector.agentNumber', 'MatchingDocument',
    'reportNumber', 'updatedAt', 'Region', 'District', 'NationalIdentificationNumber', 'ModeOfUse',
    'LastName', 'FirstName', 'Gender', 'Relation to the household', 'collector.profile.firstName',
    'SecondaryPhoneNr', 'Email', 'HouseholdMembers', 'ManNr.', 'NIDApossession', 'Term', 'Sign',
    'men15-60y', 'Men>60y', 'WomenNr', 'Women15to60y', 'Womenbet.14&18yo', 'webUser', 'RegisterdDocument',
    'n. children', 'Total n. children (<14 yo)', 'MultipleStoves', 'CookstoveType', 'contract.paygNumber',
    'CookstoveType2', 'CookstoveType3', 'FuelType', 'FuelType2', 'PerdayMeals', 'ContractPic',
    'HealthProblems', 'FirewoodCollect&Buy', 'IncomeSource', 'Income', 'VulnerabilityFactor',
    'BaselineSurvey', 'GPS', 'PicStove', 'Eligible', 'DocumentType', 'DocumentNumber', 'timestamp',
    'DocPic', 'PicNIDA', 'PicStove2', 'PicStove3', 'DocumentType', 'MoneyforFirewood', 'clientNumber',
    'HoursFuelCollection', 'client.village', 'MiddleName', 'SecondaryMobile', 'Birthday', 'collector'
]

    # Add to df the column 'signingDate' from df2 matching clientNumber with 'client.clientNumber'. Don't add the column 'clientNumber'

    df = df.merge(df2[['clientNumber', 'signingDate']], left_on='client.clientNumber', right_on='clientNumber', how='left')

    # Convert signingDate from British (DD/MM/YYYY) to international (DD-MM-YYYY)
    df['signingDate'] = (
    pd.to_datetime(df['signingDate'], errors='coerce')
      .dt.strftime('%d/%m/%Y')
)


    # Delete the queried columnes (if they exist)
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    # Keep only the lines between first_line & last_line
    #df = df.iloc[first_line:last_line]

    return df