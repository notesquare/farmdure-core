from pathlib import Path

import pandas as pd
import hdf5plugin
import xarray as xr


OBS_DATA_FP = Path('/obs_data') / 'doy_20years.nc'
SQM_DATA_PATH = Path('/sqm_data')


def get_weather_df(csv_fp):
    raw_df = pd.read_csv(csv_fp,
                         encoding='utf-8')

    if 'tmax' not in raw_df.columns or 'tmin' not in raw_df.columns:
        print('Incomplete weather data given: tmax or tmin is missing')
    # fix na values
    if raw_df[['tmax', 'tmin']].isna().sum().sum() != 0:
        print('Incomplete weather data given: nan found in tmax or tmin')

    # yearly averaged weather data
    return raw_df.reset_index(drop=True)[['doy', 'year', 'tmax', 'tmin']]


def get_weather_df_from_climate(coord, scenario='present'):
    if scenario == 'present':
        fp = OBS_DATA_FP
    else:
        fp = SQM_DATA_PATH / 'ACCESS-CM2.nc'

    with xr.open_dataset(fp, engine='h5netcdf') as ds:
        x, y = coord
        _ds = ds.sel({'latitude': y, 'longitude': x}, method='nearest')

        if scenario != 'present':
            data = _ds.sel(
                year=((_ds.year >= int(2030)) & (_ds.year <= int(2050))),
                scenario=scenario  # ex) 'ssp585'
            )
        else:
            data = _ds

        df = data.to_dataframe()\
            .reset_index()\
            .sort_values(['year', 'doy'])\
            .reset_index(drop=True)
    return df[['doy', 'year', 'tmax', 'tmin']]