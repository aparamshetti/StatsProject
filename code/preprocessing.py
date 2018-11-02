import json
import pandas as pd


json_columns = ['device', 'geoNetwork', 'totals', 'trafficSource']
data = pd.read_csv('data/train.csv', header=0, converters={column: json.loads for column in json_columns},
                   dtype={'fullVisitorId': 'str', 'visitId': 'str'})

for column in json_columns:
    flattened_data = pd.io.json.json_normalize(data[column])
    flattened_data.columns = [column + '.' + subcol for subcol in flattened_data.columns]
    data = data.drop(column, axis=1).merge(flattened_data, right_index=True, left_index=True)

data.replace({'not available in demo dataset': 'N/A', '(not set)': 'N/S', '(not provided)': 'N/P'}, inplace=True)

# parse the date column and extract day, month and year
data['date'] = pd.to_datetime(data['date'], format='%Y%m%d')
data['year'], data['month'], data['day'] = data['date'].dt.year, data['date'].dt.month, data['date'].dt.day

# drop columns that are not populated
data.dropna(axis='columns', inplace=True)

# drop date column
data.drop(axis='columns', columns=['date'], inplace=True)

data.to_csv('data/train-processed.csv', index=False)
