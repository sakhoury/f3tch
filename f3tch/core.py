"""The main entry point.
"""
# standard imports
from datetime import datetime
from typing import List, Union
from os import path
from matplotlib import pyplot

#custom imports
from f3tch import exceptions, plots
from .prometheus import Prometheus
from .query_object import Query
from .status import ExitStatus
from .utils import shorten_metric_name


def process(prometheus_obj, metric, save_data, plot_data):
    """This function processes each query metric object as follows:
     - retrieve the time-series data
     - save time-series data (save_data==True)
     - plot time-series data (plot_data==True)

    Args:
        prometheus_obj (Prometheus): prometheus pod object
        metric (dictionary): metric information to query prometheus
        save_data (boolean): Set to True to save time-series data retrieved
        plot_data (boolean): Set to True to plot the time-series data
    """
    metric_name = metric["metric_name"]
    from_timestamp = metric["from_timestamp"]
    to_timestamp = metric["to_timestamp"]
    time_series_df = prometheus_obj.get_time_series(
        metric_name=metric_name,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
        step_size=metric["step_size"])

    if save_data:
        current_timestamp = int(datetime.now().timestamp())
        filename = f"{shorten_metric_name(metric_name)}_{from_timestamp}-\
            {to_timestamp}_{current_timestamp}.csv"
        time_series_df.to_csv(filename, sep=",", header=True)

    plot_title = metric["plot_title"]
    plot_filename = metric["plot_filename"]
    if plot_data:
        plots.plot_timeseries(time_series=time_series_df,
                                   metric_name=metric_name,
                                   moving_avg_window_size=metric["moving_window"],
                                   time_slices=metric["time_slices"],
                                   plot_title=plot_title,
                                   plot_filename=plot_filename,
                                   plot_color=metric["plot_color"])

    if metric.get("plot_time_slices_overlaid", False):
        fname, ext = path.splitext(plot_filename)
        plots.plot_time_slices_overlaid(time_series=time_series_df,
                                   metric_name=metric_name,
                                   moving_avg_window_size=metric["moving_window"],
                                   time_slices=metric["time_slices"],
                                   plot_title=f"{plot_title} (unified time-axis)",
                                   plot_filename=f"{fname}_overlaid{ext}")

    plot_time_slices_discontiguous = metric.get("plot_time_slices_discontiguous", None)
    if plot_time_slices_discontiguous is not None:
        fname, ext = path.splitext(plot_filename)
        x_spacing = plot_time_slices_discontiguous.get("spacing_between_slices", 10)
        x_axis_tick_rotation = plot_time_slices_discontiguous.get("x_axis_tick_rotation", 90)
        plots.plot_time_slices_discontiguous(time_series=time_series_df,
                                   metric_name=metric_name,
                                   moving_avg_window_size=metric["moving_window"],
                                   time_slices=metric["time_slices"],
                                   plot_title=f"{plot_title} (discreet time-axis)",
                                   plot_filename=f"{fname}_discontiguous{ext}",
                                   x_spacing=x_spacing,
                                   x_tick_rotation=x_axis_tick_rotation)

def main(
    args: List[Union[str, bytes]]
) -> ExitStatus:
    """This is the main function that is responsible for connecting to
    and querying the Prometheus pod.

    Args:
        args (List[Union[str, bytes]], optional): cli arguments.

    Returns:
        ExitStatus: _description_
    """
    verbose = args.verbose if args.verbose is not None else False

    # Parse the data specification JSON-formated file
    try:
        qry = Query(filename=args.data_spec_file)

    except (exceptions.InvalidQueryFileFormat,
            exceptions.QueryFileNotLoaded) as error:
        print(f"Error: unable to parse query object file.\n{error}")
        return ExitStatus.ERROR

    # Create prometheus object
    try:
        prometheus_obj = Prometheus(
            kubeconfig=args.kubeconfig, verbose=verbose)

    except (exceptions.OpenshiftConnectionFailure,
            exceptions.PrometheusPodNotFound) as error:
        print(f"Error: {error}")
        return ExitStatus.ERROR

    for metric in qry.get_metrics():
        process(prometheus_obj=prometheus_obj,
                metric=metric,
                plot_data=qry.is_plot_data_enabled(),
                save_data=qry.is_save_fetched_data_enabled())

    if qry.is_plot_data_enabled():
        pyplot.show()

    return ExitStatus.SUCCESS
