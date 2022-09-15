"""The main entry point.
"""

# standard imports
import argparse
import sys

#custom imports
from f3tch import core
from f3tch.status import ExitStatus


def get_parser():
    """Creates a new argument parser.

    Returns:
        (argparse.ArgumentParser): argument parser for f3tch project
    """
    parser = argparse.ArgumentParser("f3tch")
    parser.add_argument("-k", "--kubeconfig", dest="kubeconfig", required=True,
                        help="kubeconfig file path")
    parser.add_argument("-d", "--data-specification", dest="data_spec_file", required=True,
                        help="JSON formatted data specification file")
    parser.add_argument("-v", "--verbose", dest="verbose", action='store_true',
                        help="Verbose flag to display additional information")

    return parser


def main(args=None):
    """Main entry point for f3tch project.

    Args:
        args (list, optional): A list of arguments as if they were input in the
          command line. Defaults to None.

    Returns:
        (int): exit code
    """
    try:
        parser = get_parser()
        args = parser.parse_args(args)
        exit_status = core.main(args=args)
    except argparse.ArgumentError as error:
        print(f"Error: invalid argument.\n{error}")
        exit_status = ExitStatus.ERROR
    return exit_status.value


if __name__ == '__main__':  # pragma: nocover
    sys.exit(main())
