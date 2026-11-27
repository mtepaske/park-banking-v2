from datetime import date
from datetime import datetime as dt
from zoneinfo import ZoneInfo


def get_today() -> date:
    """
    Get todays date

    Returns
    -------
    date
    """

    return dt.now(ZoneInfo("Australia/Melbourne")).date()


def start_of_fy(day: date | None = None) -> date:
    """
    Get the start of the fincial year

    Parameters
    ----------
    day : date | None
        The date to find the fincial year for. Defaults to todays date

    Returns
    -------
    date
    """

    if day is None:
        day = get_today()

    if day.month >= 7:
        return date(day.year, 7, 1)
    else:
        return date(day.year - 1, 7, 1)


def end_of_fy(day: date | None = None) -> date:
    """
    Get the end of the fincial year

    Parameters
    ----------
    day : date | None
        The date to find the fincial year for. Defaults to todays date

    Returns
    -------
    date
    """

    if day is None:
        day = get_today()

    if day.month >= 7:
        return date(day.year + 1, 6, 30)
    else:
        return date(day.year, 6, 30)


def get_date_from_str(date: str) -> date:
    """
    Convert a string to a date object

    Parameters
    ----------
    date : str
        The date string to convert

    Returns
    -------
    date
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


def get_str_from_date(date: date) -> str:
    """
    Convert a date object to a string in ISO format

    Parameters
    ----------
    date : date
        The date to convert

    Returns
    -------
    str
    """

    return date.strftime("%Y-%m-%d")
