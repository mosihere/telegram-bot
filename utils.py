import re
from typing import Dict
from datetime import datetime


MOVIE_INFO_URL = 'https://www.omdbapi.com'
BASE_URL = 'https://www.f2mex.ir'



def clean_movie_name_for_api(movie_name: str) -> str:
    """
    Removes the year suffix (e.g., '-2024') from the movie name if present.

    Args:
        movie_name: str
    
    Returns:
        str: Cleaned Movie name without the year suffix.
    """

    if len(movie_name) > 5 and movie_name[-5] == '-' and movie_name[-4:].isdigit():
        return movie_name[:-5]
    
    return movie_name


def get_datetime_info(compatible_with_db = False) -> Dict | str:
    """
    Getting Current Datetime Info
    return as dictionary if compatible_with_db is False
    and return strftime if True
    
    Args:
        compatible_with_db: bool

    Returns:
        Dict | str
    """

    datetime_info = datetime.now()

    if compatible_with_db:
        return datetime_info.strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'year': datetime_info.year,
        'month': datetime_info.month,
        'day': datetime_info.day,
        'hour': datetime_info.hour,
        'minute': datetime_info.minute,
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