"""Prometheus related functionality for connecting and fetching time-series data.

Raises:
    exceptions.OpenshiftConnectionFailure: failure to connect to OpenShift cluster in the
    given kubeconfig file
    exceptions.PrometheusPodNotFound: unable to locate the Prometheus pod
    exceptions.TimeseriesConversionFailure: failed to convert time-series array to data frame
"""
# standard imports
import json
import urllib
import openshift
import numpy as np

# custom imports
from f3tch import exceptions, timeseries


class Prometheus:
    """Prometheus class defintion
    """

    def __init__(self, kubeconfig,
                 prometheus_fqname="openshift-monitoring:pod/prometheus-k8s-0", verbose=False):
        """Intialization function

        Args:
            kubeconfig (str): path to kube-config file for the OpenShift cluster being queried
            prometheus_fqname (str, optional): fully qualified Prometheus pod name.
                Defaults to "openshift-monitoring:pod/prometheus-k8s-0".
            verbose (bool, optional): Set to True to show detailed processing information.
                Defaults to False.

        Raises:
            exceptions.OpenshiftConnectionFailure: failure to connect to OpenShift cluster in the
                given kubeconfig file
            exceptions.PrometheusPodNotFound: unable to locate the Prometheus pod
        """
        self.verbose = verbose

        openshift.set_default_kubeconfig_path(kubeconfig)
        try:
            self.server_version = openshift.get_server_version()
        except openshift.model.OpenShiftPythonException as exc:
            raise exceptions.OpenshiftConnectionFailure from exc

        self.__print(f"Successfully connected to OpenShift cluster running version \
            {self.server_version}!")
        # Identify the Prometheus pod
        self.__print("Detecting prometheus pod...")
        self.prometheus_pod = self.__get_prometheus_pod(prometheus_fqname)
        if self.prometheus_pod is None:
            raise exceptions.PrometheusPodNotFound

        self.__print(f"Prometheus pod found: {self.prometheus_pod}")

    def __print(self, msg):
        """Private method to display verbose information.

        Args:
            msg (str): Information to be displayed
        """
        if self.verbose:
            print(msg)

    def __get_prometheus_pod(self, prometheus_fqname):
        """The following function retrieves a prometheus pod for a given context

        Args:
            prometheus_fqname (str): Fully qualified name of Prometheus pod

        Returns:
            openshift.pod object: Prometheus pod object for the given OpenShift cluster
        """
        prometheus_pod = None

        with openshift.client_host():
            for node_name in openshift.selector('nodes').qnames():
                self.__print(
                    f"Searching node {node_name} for prometheus pod...")
                for pod_obj in openshift.get_pods_by_node(node_name):
                    if pod_obj.fqname() == prometheus_fqname:
                        prometheus_pod = pod_obj
                        break
        return prometheus_pod

    def get_time_series(self, metric_name, from_timestamp, to_timestamp, step_size):
        """This function queries the given prometheus pod and retrieves the specified 
            metric_name for the specified interval (from_timestamp, to_timestamp)

        Args:
            metric_name (str): metric qualifier to be retrieved from Prometheus
            from_timestamp (int): Starting Unix timestamp
            to_timestamp (int): Ending Unix timestamp
            step_size (int): Step size specified in seconds

        Raises:
            exceptions.PrometheusPodNotFound: unable to locate the Prometheus pod
            exceptions.TimeseriesConversionFailure: failed to convert time-series array to 
                Pandas.DataFrame object

        Returns:
            time-series data (Pandas.DataFrame): Time-series data retrieved for the specified 
                metric_name
        """
        if self.prometheus_pod is None:
            raise exceptions.PrometheusPodNotFound

        time_series = None
        time_step = f"{step_size}s"

        query_str = "http://localhost:9090/api/v1/query_range?query={}&start={}&end={}&step={}"
        query = query_str.format(urllib.parse.quote(metric_name), from_timestamp, to_timestamp,
                                 time_step)

        res = self.prometheus_pod.execute(  # pylint: disable=E1101
            cmd_to_exec=['curl', query], auto_raise=True)

        if res.status() == 0:
            if isinstance(res.out(), str):
                output = json.loads(res.out(), strict=False)
            else:
                output = res.out()

            status = output.get("status", None)
            data = output.get("data", None)
            if status is not None:
                if (status == "success") and (data is not None):
                    _results = data.get("result", [])
                    if len(_results) > 0:
                        time_series = []
                        for _result in _results:
                            _values = np.asarray(
                                _result.get("values", []), float)
                            self.__print(f"{_values.shape} results were returned for {metric_name} \
                                between {from_timestamp} and {to_timestamp}.")
                            time_series.extend(_values)
                    else:
                        self.__print(f"No results were returned for {metric_name} between \
                            {from_timestamp} and {to_timestamp}.")
                elif status == "error":
                    error = output.get("error", "")
                    print(f"Error: Time series data could not be retrieved! The following error \
                        was incurred: {error}")
        else:
            print(f"Failed to retrieve the timeseries data for {metric_name} \
                between {from_timestamp} and {to_timestamp}.")
        if (time_series is not None) and (len(time_series) > 0):
            try:
                time_series = timeseries.array_to_dataframe(arr_time_series=time_series,
                                                            metric_name=metric_name)
            except Exception as exc:
                raise exceptions.TimeseriesConversionFailure from exc
        return time_series
