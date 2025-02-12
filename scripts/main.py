import requests
import pandas as pd
import json
from io import StringIO

# Step 1: Retrieve the dataset version metadata.
version_url = "https://api.beta.ons.gov.uk/v1/datasets/retail-sales-index/editions/time-series/versions/32"
response = requests.get(version_url)

if response.status_code != 200:
    print(f"Failed to retrieve dataset version metadata. HTTP Status: {response.status_code}")
    exit(1)

data = response.json()

# Step 2: Inspect the downloads field.
downloads = data.get("downloads")
if not downloads:
    print("No downloads field found in the metadata.")
    exit(1)

print("Available download links:")
print(json.dumps(downloads, indent=2))

# Step 3: Use the CSV download link if available.
csv_link_info = downloads.get("csv")
if not csv_link_info:
    print("No CSV download link available.")
    exit(1)

# Extract the URL from the dictionary.
csv_url = csv_link_info.get("href")
print("Downloading CSV data from:", csv_url)
csv_response = requests.get(csv_url)

if csv_response.status_code != 200:
    print(f"Failed to download CSV data. HTTP Status: {csv_response.status_code}")
    exit(1)

# Step 4: Load the CSV data into a Pandas DataFrame.
csv_data = StringIO(csv_response.text)
df = pd.read_csv(csv_data)

# Display the first few rows of the DataFrame.
print("Data preview:")
print(df.head())

# (Optional) Save the DataFrame to a CSV file locally.
# df.to_csv("retail_sales_index_data.csv", index=False)

