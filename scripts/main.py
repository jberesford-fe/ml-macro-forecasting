import pandas as pd
import requests
from io import StringIO
import seaborn as sns
from neuralprophet import NeuralProphet
import numpy as np

# Monkey-patch: if np.NaN is missing, set it to np.nan
if not hasattr(np, 'NaN'):
    np.NaN = np.nan

# Download the dataset metadata and CSV URL
version_url = "https://api.beta.ons.gov.uk/v1/datasets/retail-sales-index/editions/time-series/versions/32"
response = requests.get(version_url)
response.raise_for_status()  # Raises an exception for HTTP errors
data = response.json()

# Extract the CSV download URL and download the CSV data.
csv_url = data["downloads"]["csv"]["href"]
csv_response = requests.get(csv_url)
csv_response.raise_for_status()

df = pd.read_csv(StringIO(csv_response.text))

df_mom = df[
    (df['type-of-prices'] == "chained-volume-percentage-change-on-previous-month") & 
    (df['sic-unofficial'] == "all-retailing-including-automotive-fuel")
].sort_values('mmm-yy')

df_mom['ds'] = pd.to_datetime('01-' + df_mom['mmm-yy'], format='%d-%b-%y')

df_agg = df_mom[['ds', 'v4_1']].copy()
df_agg.columns = ['ds', 'y']

df_input = df_agg.sort_values('ds').dropna().reset_index(drop=True)

min_train_size = 12*15
results = []

for i in range(min_train_size, len(df_input)):
    # Use data up to, but not including, the i-th row for training.
    train_data = df_input.iloc[:i].copy()
    
    # The actual observation we wish to forecast is at index i.
    actual_date = df_input.iloc[i]['ds']
    actual_value = df_input.iloc[i]['y']
    
    # Initialize and train the NeuralProphet model on the training data.
    m = NeuralProphet()
    # Adjust epochs as needed for speed/accuracy (here using 100 epochs for demonstration)
    m.fit(train_data, freq='MS', epochs=100, progress='none')
    
    # Create a future dataframe to forecast one period ahead (the next month).
    future = m.make_future_dataframe(train_data, periods=1)
    forecast = m.predict(future)
    
    # Extract the forecast for the actual_date.
    forecast_row = forecast.loc[forecast['ds'] == actual_date]
    if not forecast_row.empty:
        forecast_value = forecast_row['yhat1'].values[0]
    else:
        forecast_value = np.nan
    
    results.append({'ds': actual_date, 'y': actual_value, 'forecast': forecast_value})

# Create the output dataframe containing ds, y, and the forecast value.
results_df = pd.DataFrame(results)

# Optionally, plot the actual vs. forecast values.
sns.lineplot(data=results_df, x='ds', y='y', label='Actual')
sns.lineplot(data=results_df, x='ds', y='forecast', label='Forecast')

print(results_df.tail(13))
