import json
import pandas as pd


columns_of_interest = ['channelGrouping', 'fullVisitorId', 'socialEngagementType', 'visitId', 'visitNumber',
                       'device.browser', 'device.browserSize', 'device.browserVersion', 'device.deviceCategory',
                       'device.flashVersion', 'device.isMobile', 'device.language', 'device.mobileDeviceBranding',
                       'device.mobileDeviceInfo', 'device.mobileDeviceMarketingName', 'device.mobileDeviceModel',
                       'device.mobileInputSelector', 'device.operatingSystem', 'device.operatingSystemVersion',
                       'device.screenColors', 'device.screenResolution', 'geoNetwork.city', 'geoNetwork.cityId',
                       'geoNetwork.continent', 'geoNetwork.country', 'geoNetwork.latitude', 'geoNetwork.longitude',
                       'geoNetwork.metro', 'geoNetwork.networkDomain', 'geoNetwork.networkLocation', 'geoNetwork.region',
                       'geoNetwork.subContinent', 'totals.bounces', 'totals.hits', 'totals.newVisits', 'totals.pageviews',
                       'totals.sessionQualityDim', 'totals.timeOnSite', 'totals.totalTransactionRevenue',
                       'totals.transactionRevenue', 'totals.transactions', 'totals.visits', 'trafficSource.adContent',
                       'trafficSource.adwordsClickInfo.adNetworkType', 'trafficSource.adwordsClickInfo.criteriaParameters',
                       'trafficSource.adwordsClickInfo.gclId', 'trafficSource.adwordsClickInfo.isVideoAd',
                       'trafficSource.adwordsClickInfo.page', 'trafficSource.adwordsClickInfo.slot', 'trafficSource.campaign',
                       'trafficSource.isTrueDirect', 'trafficSource.keyword', 'trafficSource.medium', 'trafficSource.referralPath',
                       'trafficSource.source', 'year', 'month', 'weekday', 'hour']

json_columns = ['device', 'geoNetwork', 'totals', 'trafficSource']


def process_records(filename, output, iteration):
    skiprows = 0
    header = True
    mode = 'w'

    if iteration != 0:
        skiprows = range(1, 1 + (iteration * 100000))
        header = False
        mode = 'a'

    data = pd.read_csv(filename, header=0, converters={column: json.loads for column in json_columns},
                   dtype={'fullVisitorId': 'str', 'visitId': 'str'}, nrows=100000, skiprows=skiprows)

    # drop the columns customDimensions and hits
    data.drop(columns=['customDimensions', 'hits', 'date'], inplace=True)

    for column in json_columns:
        flattened_data = pd.io.json.json_normalize(data[column])
        flattened_data.columns = [column + '.' + subcol for subcol in flattened_data.columns]
        data = data.drop(column, axis=1).merge(flattened_data, right_index=True, left_index=True)

    data.replace({'not available in demo dataset': 'N/A', '(not set)': 'N/S', '(not provided)': 'N/P'}, inplace=True)

    # parse the date column and extract day, month and year
    data['visitStartTime'] = pd.to_datetime(data['visitStartTime'], unit='s')
    data['year'], data['month'], data['dayofweek'], data['hour'] = data['visitStartTime'].dt.year, data['visitStartTime'].dt.month, \
                                                data['visitStartTime'].dt.weekday, data['visitStartTime'].dt.hour

    # drop date column
    data.drop(axis='columns', columns=['visitStartTime'], inplace=True)
    data = data[columns_of_interest]
    data.to_csv(output, index=False, header=header, mode=mode)
    print('Iteration', iteration, ': Processed', data.shape[0], 'records')

    return data.shape[0]


if __name__ == '__main__':
    # recursive load
    iter = 0
    input_file = '../data/train_v2.csv'
    output_file = '../data/train-processed-v2.csv'
    final_file = '../data/train-v2.csv'

    while True:
        shape = process_records(input_file, output_file, iter)

        if shape != 100000:
            break

        iter = iter + 1

    data = pd.read_csv(output_file, header=0, dtype={'fullVisitorId': 'str', 'visitId': 'str'},
                       na_values=['N/S', 'N/P'])
    data.dropna(axis='columns', how='all', inplace=True)
    data['isWeekend'] = (data['dayofweek'] > 4).astype(int)
    data.to_csv(final_file, header=True, index=False)
