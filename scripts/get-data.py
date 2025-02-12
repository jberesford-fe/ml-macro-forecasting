import requests
import pandas as pd
from io import StringIO

# Retrieve dataset version metadata.
version_url = "https://api.beta.ons.gov.uk/v1/datasets/retail-sales-index/editions/time-series/versions/32"
response = requests.get(version_url)
response.raise_for_status()  # Raises an exception for HTTP errors
data = response.json()

# Extract the CSV download URL.
csv_url = data["downloads"]["csv"]["href"]

# Download the CSV data.
csv_response = requests.get(csv_url)
csv_response.raise_for_status()

# Load CSV data into a DataFrame.
df = pd.read_csv(StringIO(csv_response.text))

# Display the first few rows.
print(df.head())
