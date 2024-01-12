import pandas as pd
import numpy as np

def format_row(row):
    # Define the format for each column
    format_spec = [
        "{:<40}",  # Description
        "{:>20}",  # 1-Jan-23
        "{:>20}",  # Net Change
        "{:>20}",  # 30-Mar-23
        "{:<30}"   # For More Information
    ]

    # Apply the format to each element in the row
    formatted_row = [fmt.format(item) if item != '' else fmt.format('') for fmt, item in zip(format_spec, row)]

    # Join the formatted elements with spaces
    return ''.join(formatted_row)

def process_chunk(chunk_data):
    # Replace NaN values with empty strings
    chunk_data_filled = chunk_data.replace(np.nan, '', regex=True)

    # Initialize an empty list to store formatted rows
    formatted_rows = []

    # Iterate over each row in the DataFrame
    for index, row in chunk_data_filled.iterrows():
        formatted_row = format_row(row)
        formatted_rows.append(formatted_row)

    # Combine all rows into a single string
    combined_rows = '\n'.join(formatted_rows)

    return combined_rows

# Path to your Excel file
excel_file = 'Sample Financials Data - Balance Sheet.xlsx'

# Read the entire Excel file
df = pd.read_excel(excel_file)
formatted_output = process_chunk(df)

# Write to output file
with open("formatted.txt", 'w', encoding='utf-8') as file:
    file.write(formatted_output)
