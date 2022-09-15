"""Utility functions
"""

#standard imports
from datetime import datetime
import pandas as pd


def convert_time(timestamp):
    """Convert Unix timestamp to string formatted time

    Args:
        timestmap (float): Unix timestamp

    Returns:
        (str): string formmatted timestamp
    """
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def strtime_to_timestamp(strtime):
    """This functions converts a datetime string variable to a Unix timestamp
        Example: '18.05.2022 16:08:05' -> 1652904485

    Args:
        strtime (str): datetime string formatted timestamp (%d.%m.%Y %H:%M:%S)

    Returns:
        (int): Unix timestamp
    """
    return int(datetime.strptime(strtime, '%d.%m.%Y %H:%M:%S').timestamp())


def transform_dataframe_time_column(time_series_df):
    """Transform Pandas.DataFrame time-series timestamp column

    Args:
        time_series_df (Pandas.DataFrame): Time-series DataFrame object with
            columns=['timestamp','<metric_name>']

    Returns:
        (Pandas.DataFrame): Timestamp-formatted DataFrame
    """
    assert "timestamp" in time_series_df.columns
    time_series_df.timestamp = time_series_df.timestamp.apply(
        lambda y: datetime.fromtimestamp(y).strftime('%Y-%m-%d %H:%M:%S')).astype("datetime64")
    return time_series_df


def date_filter(time_series_df, date_range):
    """Filter Pandas.DataFrame by timestamps for given date_range

    Args:
        time_series_df (Pandas.DataFrame): Time-series DataFrame object with
            columns=['timestamp','<metric_name>']
        date_range (list): List of two timestamps: [start_timestamp, end_timestamp]

    Returns:
        (Pandas.DataFrame): filtered time-series DataFrame
    """
    assert strtime_to_timestamp(date_range[0]) < strtime_to_timestamp(date_range[1]), \
        f"{date_range[0]} should be less than {date_range[1]}"

    date_range_df = transform_dataframe_time_column(
        time_series_df=pd.DataFrame([strtime_to_timestamp(_) for _ in date_range], columns=["timestamp"]))

    return time_series_df.loc[(time_series_df.index >= date_range_df.timestamp[0]) &
                              (time_series_df.index < date_range_df.timestamp[1])]


def shorten_metric_name(metric_name, MAX_METRIC_NAME_LEN=50):
    """Function to reduce metric-names that are longer than MAX_METRIC_NAME_LEN chars

    Args:
        metric_name (str): metric-name
        MAX_METRIC_NAME_LEN (int, optional): Maximum length of metric-name. Defaults to 50.

    Returns:
        (str): metric-name if metric-name is less than MAX_METRIC_NAME_LEN chars long, otherwise
            returns truncated metric-name of length = MAX_METRIC_NAME_LEN chars
    """
    return metric_name if len(metric_name) < MAX_METRIC_NAME_LEN \
        else f"{metric_name[0:MAX_METRIC_NAME_LEN]}_capped"
