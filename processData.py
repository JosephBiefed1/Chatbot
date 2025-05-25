import pandas as pd
from preprocess import *

def classifyData(filepath: str = 'data/new_classified_messages_2.csv'):
    df = pd.read_csv(filepath)  # Read the CSV file into a DataFrame call
    df = df.iloc[:1000]  # Limit to first 5000 rows for testing
    output = []
    error_log = []
    for msg in df['Message']:
        result = classify_message(msg)
        if result[2] == "Error":
            error_log.append((msg, result[1]))
        output.append(result[0:2])
        
    df['Crowd Level'] = [i[0] for i in output]
    df['Direction'] = [i[1] for i in output]

    df.to_csv('data/new_classified_messages_2.csv', index=False)