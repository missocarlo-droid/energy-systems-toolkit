import pandas as pd

def cleaning_csv(input_file):

    cols_to_drop = [
    'client.status', 'timestamp', 'collector.profile.lastName', 'collector.agentNumber',
    'reportNumber', 'updatedAt', 'Region', 'District', 'NationalIdentificationNumber',
    'LastName', 'FirstName', 'Gender', 'Relation to the household', 'collector.profile.firstName',
    'SecondaryPhoneNr', 'Email', 'HouseholdMembers', 'ManNr.', 'NIDApossession',
    'men15-60y', 'Men>60y', 'WomenNr', 'Women15to60y', 'Womenbet.14&18yo',
    'n. children', 'Total n. children (<14 yo)', 'MultipleStoves', 'CookstoveType',
    'CookstoveType2', 'CookstoveType3', 'FuelType', 'FuelType2', 'PerdayMeals',
    'HealthProblems', 'FirewoodCollect&Buy', 'IncomeSource', 'Income', 'VulnerabilityFactor',
    'BaselineSurvey', 'GPS', 'PicStove', 'Eligible', 'DocumentType', 'DocumentNumber',
    'DocPic', 'PicNIDA', 'PicStove2', 'PicStove3', 'DocumentType', 'MoneyforFirewood',
    'HoursFuelCollection', 'client.village', 'MiddleName', 'SecondaryMobile', 'Birthday'
]

    # Read the file
    df = input_file

    # Strip whitespace and potential BOM from column names
    df.columns = df.columns.str.replace('\ufeff', '', regex=False)

    # Delete the queried columnes (if they exist)
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

    return df
