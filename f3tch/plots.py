"""Time-series plotting functions
"""

# standard imports
import math
from matplotlib import pyplot
import numpy as np

# custom imports
from f3tch import utils

# pylint: disable=too-many-arguments
# pylint: disable-msg=too-many-locals


def plot_timeseries(time_series, metric_name, moving_avg_window_size=0, time_slices=None,
                    plot_title="Time Series Plot", plot_minmax=False, plot_filename="",
                    plot_color="blue", verbose=False):
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
    if time_series is None:
        return

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
    axis = pyplot.gca()
    # Labelling the axes and setting a title
    pyplot.xlabel("Date/Time")
    pyplot.ylabel(metric_name_lbl)
    pyplot.title(plot_title)

    # Plot the metric column
    y_vals = vals[moving_avg_window_size:]
    axis.plot(y_vals, label=metric_name_lbl, color=plot_color)

    # Plot time_slices if specified
    if time_slices is not None:
        for time_slice in time_slices:
            tmp_df = utils.date_filter(
                time_series_df=vals, date_range=time_slice['time_range'])
            tmp_df = tmp_df.loc[tmp_df.index >= y_vals.index.values[0]]
            lbl = time_slice["label"]
            axis.plot(tmp_df, label=f"{lbl}_{metric_name_lbl}",
                      color=time_slice['color'])

    # Plot moving average
    if moving_avg_window_size > 0:
        axis.plot(
            vals_avg, label=f"moving_avg_{metric_name_lbl}", color='orchid')
        axis.plot(vals_avg+vals_stdev, ':', label=f"moving_stdev_{metric_name_lbl}",
                  color='crimson')
        axis.plot(vals_avg-vals_stdev, ':', color='crimson')

        if plot_minmax:
            axis.plot(vals_min, label=f"moving_min_{metric_name_lbl}", color='darkturquoise',
                      alpha=0.4)
            axis.plot(vals_max, label=f"moving_max_{metric_name_lbl}", color='orangered',
                      alpha=0.4)
    pyplot.legend()
    if plot_filename != "":
        pyplot.savefig(plot_filename, bbox_inches='tight', dpi=300)
    pyplot.draw()


def sort_time_slices(time_slices):
    """Sort time-slices array in ascending time-slice order

    Args:
        time_slices (list[map]): list of time-slices

    Returns:
        list[map]: sorted time-slice array
    """
    return sorted(time_slices, key=lambda x: x.get('time_range')[0], reverse=False)


def get_sample_idx(num_indices, num_samples):
    """Generate sample indices

    Args:
        num_indices (int): number of indices
        num_samples (int): number of samples

    Returns:
        list(int): array of sample indices
    """
    sample_idx = []
    for i in range(num_indices):
        if i % num_samples == 0:
            sample_idx.append(i)
    return sample_idx


def process_time_slice_data(time_series, metric_name, time_slices, moving_avg_window_size, verbose):
    """Process time-slices

    Args:
        time_series (_type_): _description_
        metric_name (_type_): _description_
        time_slices (_type_): _description_
        moving_avg_window_size (_type_): _description_
        verbose (_type_): _description_

    Returns:
        list(map): list of processed time-slices
    """

    assert (metric_name in time_series.columns), \
        f"{metric_name} does not match given time-series!"
    assert len(time_slices) >= 1, "At least 1 time-slice object is required."

    metric_name_lbl = utils.shorten_metric_name(metric_name)

    # sort time-slices
    time_slices = sort_time_slices(time_slices=time_slices)
    vals = time_series[metric_name]

    # Compute the moving average
    if moving_avg_window_size > 0:
        aux = vals.rolling(window=moving_avg_window_size)
        vals_avg = aux.mean()
        vals_stdev = aux.std()

        if verbose:
            print(f"vals_avg.shape = {len(vals_avg)}")
            print(f"vals_stdev.shape = {len(vals_stdev)}")

    data = []
    for time_slice in time_slices:
        tmp_df = utils.date_filter(
            time_series_df=vals, date_range=time_slice['time_range'])
        lbl = time_slice["label"]

        data.append({"x": np.asarray(tmp_df.index, dtype='datetime64[m]'),
                     "y": tmp_df.to_numpy(), "lbl": f"{lbl}_{metric_name_lbl}",
                     "color": time_slice['color']})

    return data


def plot_time_slices_overlaid(time_series, metric_name, time_slices, moving_avg_window_size=0,
                              plot_title="Time Series Plot", plot_filename="", verbose=False):
    """Function to plot the time-slices data in unified time-space only using matplotlib.pyplot
    library

    Args:
        time_series (_type_): _description_
        metric_name (_type_): _description_
        time_slices (list, optional): time-slices of interest
        moving_avg_window_size (int, optional): _description_. Defaults to 0.
        plot_title (str, optional): _description_. Defaults to "Time Series Plot".
        plot_filename (str, optional): _description_. Defaults to "".
        verbose (bool, optional): _description_. Defaults to False.
    """

    if time_series is None:
        return

    metric_name_lbl = utils.shorten_metric_name(metric_name)

    # Using a in-built style to change the look and feel of the plot
    pyplot.style.use("seaborn")
    pyplot.figure()
    axis = pyplot.gca()
    # Labelling the axes and setting a title
    # pyplot.xlabel("Date/Time")
    pyplot.ylabel(metric_name_lbl)
    pyplot.title(plot_title)

    data = process_time_slice_data(
        time_series, metric_name, time_slices, moving_avg_window_size, verbose)
    for _data in data:
        axis.plot(_data["y"], label=_data["lbl"], color=_data["color"])

    pyplot.legend()
    pyplot.xticks([])

    if plot_filename != "":
        pyplot.savefig(plot_filename, bbox_inches='tight', dpi=300)
    pyplot.draw()


def plot_time_slices_discontiguous(time_series, metric_name, time_slices, moving_avg_window_size=0,
                                   plot_title="Time Series Plot", plot_filename="", x_spacing=20,
                                   x_tick_rotation=70, verbose=False):
    """Function to plot the time-slices data in discreet time-space only using matplotlib.pyplot
    library

    Args:
        time_series (_type_): _description_
        metric_name (_type_): _description_
        time_slices (list, optional): time-slices of interest
        moving_avg_window_size (int, optional): _description_. Defaults to 0.
        plot_title (str, optional): _description_. Defaults to "Time Series Plot".
        plot_filename (str, optional): _description_. Defaults to "".
        verbose (bool, optional): _description_. Defaults to False.
    """

    if time_series is None:
        return

    metric_name_lbl = utils.shorten_metric_name(metric_name)

    # Using a in-built style to change the look and feel of the plot
    pyplot.style.use("seaborn")
    pyplot.figure()
    axis = pyplot.gca()
    # Labelling the axes and setting a title
    pyplot.ylabel(metric_name_lbl)
    pyplot.title(plot_title)

    data = process_time_slice_data(
        time_series, metric_name, time_slices, moving_avg_window_size, verbose)

    start = end = 0
    _xticks = []
    for _data in data:
        start = end+x_spacing
        end += len(_data["x"])+x_spacing

        for k, xt in enumerate(range(0, x_spacing)):
            _xticks.append('')

        for k, xt in enumerate(range(start, end)):
            _xticks.append(_data["x"][k])

        axis.plot(range(start, end), _data["y"],
                  label=_data["lbl"], color=_data["color"])

    ticks = range(0, len(_xticks))
    num_samples = np.min([10, math.floor(math.sqrt(len(_xticks)))])
    sample_idx = get_sample_idx(
        num_indices=len(_xticks), num_samples=num_samples)

    axis.set_xticks([ticks[idx] for idx in sample_idx])
    axis.set_xticklabels([_xticks[idx] for idx in sample_idx])
    pyplot.xticks(rotation=x_tick_rotation)
    pyplot.legend()

    if plot_filename != "":
        pyplot.savefig(plot_filename, bbox_inches='tight', dpi=300)
    pyplot.draw()
