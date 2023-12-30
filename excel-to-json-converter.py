import pandas as pd
import json
from datetime import datetime

# Function to handle datetime serialization
def datetime_handler(x):
    if isinstance(x, datetime):
        return x.isoformat()
    raise TypeError("Unknown type")

# Custom function to convert row to dictionary and exclude null/empty values
def row_to_dict(row):
    row_dict = {}
    for key, value in row.items():
        if pd.notna(value) and value != '':
            # Convert datetime to string
            if isinstance(value, datetime):
                row_dict[key] = value.isoformat()
            else:
                row_dict[key] = value
    return row_dict

# Read the Excel file
df = pd.read_excel('Sample Financials Data - Balance Sheet.xlsx')

# Apply the function to each row
dict_rows = df.apply(row_to_dict, axis=1)

# Convert list of dictionaries to JSON
json_documents = '\n'.join(json.dumps(row, default=datetime_handler) for row in dict_rows)

# Save to a file or use directly
with open('data.json', 'w') as file:
    file.write(json_documents)
