"""Time-series related functions
"""

# standard imports
from matplotlib import pyplot
import numpy as np
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


def plot_timeseries(time_series, metric_name, moving_avg_window_size=0, time_slices=None,
                    plot_title="Time Series Plot", plot_minmax=False, plot_filename="", plot_color="blue",
                    verbose=False):
    """Function to plot the time-series data using matplotlib.pyplot library

    Args:
        time_series (_type_): _description_
        metric_name (_type_): _description_
        moving_avg_window_size (int, optional): _description_. Defaults to 0.
        time_slices (list, optional): _description_. Defaults to None.
        plot_title (str, optional): _description_. Defaults to "Time Series Plot".
        plot_minmax (bool, optional): _description_. Defaults to False.
        plot_filename (str, optional): _description_. Defaults to "".
        plot_color (str, optional): _description_. Defaults to "blue".
        verbose (bool, optional): _description_. Defaults to False.
    """
    verbose_print(verbose, f"time_series.shape = {time_series.shape}")

    assert (metric_name in time_series.columns), \
        f"{metric_name} does not match given time-series!"

    metric_name_lbl = utils.shorten_metric_name(metric_name)
    vals = time_series[metric_name]
    # Compute the moving average
    if moving_avg_window_size > 0:
        aux = vals.rolling(window=moving_avg_window_size)
        vals_avg = aux.mean()
        vals_stdev = aux.std()
        if plot_minmax:
            vals_min = aux.min()
            vals_max = aux.max()
        if verbose:
            print(f"The average {metric_name} value = {np.mean(vals)}")
            print(f"The std dev {metric_name} value = {np.std(vals)}")
            print(f"The average moving_avg value = {np.mean(vals_avg)}")
            print(f"The average moving_stdev value = {np.mean(vals_stdev)}")

    # Using a in-built style to change the look and feel of the plot
    pyplot.style.use("seaborn")
    pyplot.figure()
    ax = pyplot.gca()
    # Labelling the axes and setting a title
    pyplot.xlabel("Date/Time")
    pyplot.ylabel(metric_name_lbl)
    pyplot.title(plot_title)

    # Plot the metric column
    yy = vals[moving_avg_window_size:]
    ax.plot(yy, label=metric_name_lbl, color=plot_color)

    # Plot time_slices if specified
    if time_slices is not None:
        for time_slice in time_slices:
            tmp_df = utils.date_filter(
                time_series_df=vals, date_range=time_slice['time_range'])
            tmp_df = tmp_df.loc[tmp_df.index >= yy.index.values[0]]
            lbl = time_slice["label"]
            ax.plot(tmp_df, label=f"{lbl}_{metric_name_lbl}",
                    color=time_slice['color'])

    # Plot moving average
    if moving_avg_window_size > 0:
        ax.plot(
            vals_avg, label=f"moving_avg_{metric_name_lbl}", color='orchid')
        ax.plot(vals_avg+vals_stdev, ':', label=f"moving_stdev_{metric_name_lbl}",
                color='crimson')
        ax.plot(vals_avg-vals_stdev, ':', color='crimson')

        if plot_minmax:
            ax.plot(vals_min, label=f"moving_min_{metric_name_lbl}", color='darkturquoise',
                    alpha=0.4)
            ax.plot(vals_max, label=f"moving_max_{metric_name_lbl}", color='orangered',
                    alpha=0.4)
    pyplot.legend()
    if plot_filename != "":
        pyplot.savefig(plot_filename, bbox_inches='tight', dpi=300)
    pyplot.draw()
