import re
from typing import Dict, List
from datetime import datetime
import aiohttp
from aiohttp import ClientError, ContentTypeError



async def sanitize_payload(payload: dict) -> dict:
    """Sanitizes special characters in 'first_name' and 'last_name' fields."""

    if payload:
        payload['first_name'] = payload.get('first_name', '').encode('utf-8', errors='ignore').decode()
        payload['last_name'] = payload.get('last_name', '').encode('utf-8', errors='ignore').decode()
    return payload


async def make_request(url: str, method: str, params: dict=None, payload: dict=None) -> dict:
    """
    An async function to send HTTP request to an API endpoint based on methods
    and return awaited JSON result.

    Args:
        url (str): API endpoint URL
        method (str): HTTP method (GET, POST, PATCH, PUT, DELETE)
        params (dict, optional): Query parameters for GET requests
        payload (dict, optional): Data payload for POST, PUT, PATCH requests

    Returns:
        dict: Deserialized JSON response or error message
    """

    method = method.upper()
    async with aiohttp.ClientSession() as session:
        try:
            methods_map = {
                'GET': session.get,
                'POST': session.post,
                'PUT': session.put,
                'PATCH': session.patch,
                'DELETE': session.delete
            }                

            payload = sanitize_payload(payload)

            if method in methods_map:
                args = {'params': params} if method == 'GET' else {'json': payload}
                async with methods_map[method](url, **args) as response:
                    if response.status == 204 and method == 'DELETE':
                        return {'detail': 'record deleted successfully'}
                    return await response.json()
            else:
                return {'error': 'unsuported http method!'}
                    
        except ContentTypeError:
            print(f'method -> {method}, params -> {params}, payload -> {payload}')
            return {'error': 'Unexpected response format, expected JSON'}
        
        except ClientError as e:
            return {'error': str(e)}
        
        except Exception as e:
            return {'error': f'An unexpected error occurred: {e}'}


def clean_movie_name_for_api(movie_name: str) -> str:
    """
    Removes the year suffix (e.g., '-2024') and replace ( '-' with space) from the movie name if present.

    Args:
        movie_name: str
    
    Returns:
        str: Cleaned Movie name without the year suffix and dashes.
    """

    if len(movie_name) > 5 and movie_name[-5] == '-' and movie_name[-4:].isdigit():
        return movie_name[:-5].replace(' ', '-')
    
    return movie_name.replace(' ', '-')


def movie_data_normalizer(movies: List[Dict]) -> List[Dict]:
    """
    Get a single arg as movies
    iterate on the given list
    create a dictionary for each object
    get necessary data and append them to a new list
    finally returns a list of dict.
    
    Args:
        movies: list(dict)

    Returns:
        list(dict)
    """

    data = list()
    for movie in movies:
        movie_info = {
            'link': f'{movie.get("link")}\n',
            'quality_and_codec': f'{movie.get("quality")} - {movie.get("codec")}',
            'name': movie.get('movie_name'),
            'published_at': movie.get('movie_published_at'),
            'subtitle_url': movie.get('movie_subtitle_url'),
            }
        data.append(movie_info)

    return data


def normalized_imdb_info(movie_info: dict) -> dict:
    """
    Create a Beautiful Dictionary From JSON response

    Args:
        movie_info: dict
    
    Returns:
        dict
    """

    result = {
        '🏷️ Title': movie_info.get('Title'),
        '🗓️Year': movie_info.get('Year'),
        '🔗 Type': movie_info.get('Type'),
        'Ʀ Rated': movie_info.get('Rated'),
        '📅 Released': movie_info.get('Released'),
        '🕥 Length': movie_info.get('Runtime'),
        '📚 Genre': movie_info.get('Genre'),
        '🎬 Director': movie_info.get('Director'),
        '✍🏻 Writer': movie_info.get('Writer'),
        '🎭 Actors': movie_info.get('Actors'),
        '📖 Plot': movie_info.get('Plot'),
        '💬 Language': movie_info.get('Language'),
        '🌎 Country': movie_info.get('Country'),
        '🏅 Awards': movie_info.get('Awards'),
        '🌇 Poster': movie_info.get('Poster'),
        '📊 Metacritic': movie_info.get('Metascore'),
        '📊 imdbRating': movie_info.get('imdbRating'),
        '🗳 imdbVotes': movie_info.get('imdbVotes'),
        '💰 BoxOffice': movie_info.get('BoxOffice'),
    }
    return result


def get_last_movie_id() -> str:
    """
    Read Last Row ID from file. If the file does not exist or is empty,
    initialize it with '1' and return '1'.

    Returns:
        str: The last movie ID as a string.
    """

    try:
        with open('last_movie_id.txt', 'r') as file:
            last_row_id = file.read()
        return last_row_id
    
    except FileNotFoundError:
        with open('last_movie_id.txt', 'w') as file:
            file.write('1')
        return '1'


def update_last_movie_id(movie_id: str) -> str:
    """
    Rewrite the file with the last movie_id.

    Args:
        movie_id (str): The movie ID to be written to the file.

    Returns:
        str: The movie ID that was written to the file.
    """

    with open('last_movie_id.txt', 'w') as file:
        file.write(str(movie_id))
    return movie_id


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
        return datetime_info.strftime('%Y-%m-%dT%H:%M:%S')
    
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

    quality = re.findall(r'[0-9]{3,4}p',link)
    return quality


def find_series_season(link: str):
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