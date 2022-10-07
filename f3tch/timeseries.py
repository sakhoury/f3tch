"""Time-series related functions
"""

# standard imports
import pandas as pd

# custom imports
from f3tch import utils


def verbose_print(verbose, msg):
    """Print message if verbose flag set to True

    Args:
        verbose (bool): Set to True to display additional information
        msg (str): Information to be displayed
    """
    if verbose:
        print(msg)


def array_to_dataframe(arr_time_series, metric_name):
    """This function takes a time-series array and converts it to Pandas.DataFrame object

    Args:
        arr_time_series (numpy.array): 2-dimensional time-series array as such:
            [[t1,value1], [t2,value2], ..., [tn,valuen]]
        metric_name (str): metric name

    Returns:
        Time-series data (Pandas.DataFrame): converted Pandas.DataFrame time-series object
    """
    assert len(arr_time_series) > 0, "Given time series data is empty!"
    return utils.transform_dataframe_time_column(
        time_series_df=pd.DataFrame(arr_time_series, columns=["timestamp",
                                                              metric_name])).set_index("timestamp")
