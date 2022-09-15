"""Custom defined exceptions
"""


class OpenshiftConnectionFailure(Exception):
    """Raised when a connection cannot be established to the
    OpenShift cluster"""


class PrometheusPodNotFound(Exception):
    """Raised when the Prometheus pod cannot be identified in the given
    OpenShift cluster"""


class TimeseriesConversionFailure(Exception):
    """Raised when a time-series array cannot be converted to a
    pandas DataFrame time-series object"""


class InvalidQueryFileFormat(Exception):
    """Raised when the given query object JSON file does not conform to the
    expected format"""


class QueryFileNotLoaded(Exception):
    """Raised when a query object JSON file was not loaded successfully!"""
