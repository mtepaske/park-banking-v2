from datetime import date
from datetime import datetime as dt
from zoneinfo import ZoneInfo


def get_date_from_str(date: str) -> date:
    """
    Converts from a string to a date

    Args:
        date: The date to convert

    Returns:
        The date as a date object
    """

    try:
        parsed_date = dt.strptime(date, "%d %b %y").astimezone(
            ZoneInfo("Australia/Melbourne")
        )
    except ValueError:
        parsed_date = dt.strptime(date, "%Y-%m-%d").astimezone(
            ZoneInfo("Australia/Melbourne")
        )

    return parsed_date
