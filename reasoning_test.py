import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

openai_gpt_model_deployment_name = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT")
openai_client = AzureOpenAI(azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                            api_version="2023-05-15")

# Path to the xlsx file
file_path = 'Sample Financials Data - Balance Sheet.xlsx'

# read the second Post modelling sheet
example_input_df = pd.read_excel(file_path, nrows=50)

example_input_csv = example_input_df.to_markdown()

expected_output_df = pd.read_excel(file_path, sheet_name=1)

expected_output_csv = expected_output_df.to_markdown()

prompt = ("We need to reformat this table to only have a single header row and provide output in a right csv format: \n"
          + example_input_csv
          + "Create result table like this format without explanation: \n"
          + expected_output_csv
          + "In the result table: \n"
          + "Fund column contains a funda name from the input"
          + "Date column contains the latest date from the input"
          + "Receivables column contains a sum of values from the latest date column: Accrued Gross Income,Accrued Gross Withholding,Spot Contracts,Securities Sold,Reclaims,Prepaid Expenses or any other names synonym to"
          + "Liabilities column contains a sum of values from the latest date column: Accrued Expenses,Accrued Capital Expenses,Spot Contracts,Income, Securities Purchased"
          + "Total Net Asset column contains a value of from the latest date column: Total Net Assets"
          + "Keep empty Domestic Cash output column")
response = openai_client.completions.create(model=openai_gpt_model_deployment_name, prompt=prompt, max_tokens=200)

# Write the response to a CSV file
response_text = response.choices[0].text
csv_file_path = 'output.csv'

with open(csv_file_path, 'w') as file:
    file.write(response_text)

print("*************************Result**************************")
print(response_text)
print(f"Response written to {csv_file_path}")