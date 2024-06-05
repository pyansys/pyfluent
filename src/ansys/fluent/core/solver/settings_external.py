"""Miscellaneous utility functions."""

interruptible_commands = [
    "solution/run-calculation/iterate",
    "solution/run-calculation/calculate",
    "solution/run-calculation/dual-time-iterate",
]


def expand_api_file_argument(command_name, value, kwargs):
    """Expand API file argument."""
    if kwargs.get("file_type") == "case-data" or command_name in [
        "read_case_data",
        "write_case_data",
    ]:
        data_file = value.replace(".cas", ".dat")
        return [value, data_file]
    else:
        return [value]
