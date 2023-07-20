from pathlib import Path

import polars as pl


def verify_weather_lf(lf):
    if 'tmax' not in lf.columns or 'tmin' not in lf.columns:
        raise ValueError(
            'Incomplete weather data given: tmax or tmin is missing'
        )

    # NA not allowed
    if lf.fill_nan(None).null_count().collect().sum(axis=1).to_numpy()[0] != 0:
        raise ValueError(
            'Incomplete weather data given: missing value in tmax or tmin'
        )

    # yearly averaged weather data
    return lf


def get_weather_lf(csv_fp):
    raw_lf = pl.scan_csv(csv_fp, encoding='utf8')
    varified_lf = verify_weather_lf(raw_lf)

    return varified_lf


def get_sample_weather_data():
    csv_fp = Path(__file__).parent.parent / 'sample.csv'
    return get_weather_lf(csv_fp)
