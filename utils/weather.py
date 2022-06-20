from pathlib import Path

import pandas as pd


def get_weather_df(csv_fp=None):
    # TODO: get dataframe with coord
    if csv_fp is None:
        csv_fp = Path('../../../assets') / 'sample.csv'

    raw_df = pd.read_csv(csv_fp,
                        #  usecols=RAW_COLUMN_NAMES,
                         encoding='utf-8')

    if 'tmax' not in raw_df.columns or 'tmin' not in raw_df.columns:
        print('Incomplete weather data given: tmax or tmin is missing')
    # fix na values
    if raw_df[['tmax', 'tmin']].isna().sum().sum() != 0:
        print('Incomplete weather data given: nan found in tmax or tmin')

    # yearly averaged weather data
    return raw_df.reset_index(drop=True)[['doy', 'year', 'tmax', 'tmin']]
