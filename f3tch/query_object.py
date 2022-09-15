# standard imports
import json

# custom imports
from f3tch import exceptions, utils


class Query():
    """Query class defines the fields that need to be specified for querying 
    a Prometheus pod.
    """

    def __init__(self, filename):
        """Initialization function

        Args:
            filename (string): Full path to JSON file specifying the data
            to be retrieved.
        """
        self.required_outer_keys = ["metric_list", "step_size", "moving_window",
                                    "from_timestamp", "to_timestamp"]
        self.required_inner_keys = ["metric"]

        self.object = None
        try:
            self.object = self.__read(filename)

        except (exceptions.InvalidQueryFileFormat,
                exceptions.QueryFileNotLoaded) as error:
            print(f"Error: {error}")

    def __validate(self, obj):
        """Private function to validate the JSON data specification object 

        Args:
            obj (dictionary): JSON object read from data specification file

        Returns:
            boolean: True for valididated JSON data specification, and
            False otherwise.
        """
        for k in self.required_outer_keys:
            if k not in obj:
                return False

        for _metric in obj["metric_list"]:
            _keys = _metric.keys()
            for k in self.required_inner_keys:
                if k not in _keys:
                    return False

        if len(obj["metric_list"]) < 1:
            return False

        return True

    def __read(self, filename):
        """Read the JSON-formated query object file

        Args:
            filename (string): Full path to JSON file specifying the data

        Raises:
            exceptions.InvalidQueryFileFormat: raised for invalid JSON data specification object
            exceptions.QueryFileNotLoaded: raised when unable to read/parse JSON file

        Returns:
            dictionary: map comprising of metrics to be retrieved from Prometheus
        """
        obj = None
        with open(filename, "r", encoding="utf8") as file:
            obj = json.load(file)
            print("Query object file loaded!")

            if not self.__validate(obj=obj):
                raise exceptions.InvalidQueryFileFormat

        if obj is None:
            raise exceptions.QueryFileNotLoaded

        return obj

    def __get_attribute(self, attribute, default_value=None):
        """Get attribute from dictionary self.object

        Args:
            attribute (string): field name (key)
            default_value (object, optional): specify default value if attribute does not
            exist in self.object. Defaults to None.

        Returns:
            object: associated attribute value
        """
        if self.object is None:
            return None
        return self.object.get(attribute, default_value)

    def is_plot_data_enabled(self):
        """Check if plot_data field is set

        Returns:
            boolean: True if plot_data is enabled, else False
        """
        return self.__get_attribute(attribute="plot_fetched_data", default_value=False)

    def is_save_fetched_data_enabled(self):
        """Check if save_fetched_data field is set

        Returns:
            boolean: True if save_fetched_data is enabled, else False
        """
        return self.__get_attribute(attribute="save_fetched_data", default_value=False)

    def get_metrics(self):
        """Retrieve list of metrics from self.object

        Returns:
            List(dictionary): list of dictionaries for each metric in the JSON data specification
            file.
        """
        if self.object is None:
            return None

        default_from_timestamp = self.__get_attribute("from_timestamp")
        default_to_timestamp = self.__get_attribute("to_timestamp")
        default_step_size = self.__get_attribute("step_size")
        default_moving_window = self.__get_attribute("moving_window")
        default_plot_color = self.__get_attribute("plot_color", "blue")

        metric_list = self.__get_attribute(attribute="metric_list")

        metrics = []

        for metric in metric_list:
            metric_name = metric["metric"]
            from_timestamp = utils.strtime_to_timestamp(metric.get("from_timestamp",
                                                                   default_from_timestamp))
            to_timestamp = utils.strtime_to_timestamp(metric.get("to_timestamp",
                                                                 default_to_timestamp))
            step_size = int(metric.get("step_size", default_step_size))
            moving_window = int(metric.get(
                "moving_window", default_moving_window))
            plot_color = metric.get("plot_color", default_plot_color)
            time_slices = metric.get("time_slices", [])
            plot_title = metric.get("plot_title", "")
            plot_filename = metric.get("plot_filename", "")

            # TODO: validate time_slices # pylint: disable=W0511

            metrics.append({"metric_name": metric_name,
                            "from_timestamp": from_timestamp,
                            "to_timestamp": to_timestamp,
                            "step_size": step_size,
                            "moving_window": moving_window,
                            "plot_color": plot_color,
                            "time_slices": time_slices,
                            "plot_title": plot_title,
                            "plot_filename": plot_filename})

        return metrics
