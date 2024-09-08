from typing import Dict
from datetime import datetime



MOVIE_INFO_URL = 'https://www.omdbapi.com'
BASE_URL = 'https://www.f2mex.ir'


def get_datetime_info() -> Dict:
    datetime_info = datetime.now()

    return {
        'year': datetime_info.year,
        'month': datetime_info.month,
        'day': datetime_info.day,
        'hour': datetime_info.hour,
        'minut': datetime_info.minute,
        'second': datetime_info.second,
    }


def find_movie_quality(link: list) -> list:
    """
    Get a single arg as link
    find and return list of quality .

    Args:
        link: list

    Returns:
        list
    """

    quality = re.findall(r'[0-9]{3,4}[p]',link)
    return quality


def find_series_season(link: list):
    """
    Get a single arg as link
    find and return list of season numbers.

    Args:
        link: list

    Returns:
        list
    """
    season = re.findall(r'S\d{2}', link)
    return season