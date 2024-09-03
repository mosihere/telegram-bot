import re
import requests
from typing import List
from crawler import BASE_URL
from dal import connect_to_database



def get_movies_from_db() -> List[tuple]:
    """
    Get a Single Argument as Movie Record
    Using regex to find Poster of indicated movie.

    Args:
        record: tuple
    
    Returns:
        None
    """

    sql_command = f""" SELECT * FROM movies_movie WHERE id >= 1"""
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command)
    movies = cursor.fetchall()
    conx.close()
    return movies


def get_movie_poster_url(record: tuple) -> tuple | None:
    """
    Get a single argument as record
    Unpack result and assign them to variables
    send a get request to given URL
    find movie poster
    return that poster_url

    Args:
        record: tuple
    
    Returns:
        tuple(str, str) | None
    """

    movie_id = record[0]
    movie_url = record[2]
    movie_site_id = movie_url.split('/')[3]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(movie_url, headers=headers)
    pattern = rf'{BASE_URL}/wp-content/uploads/poster/.*/{movie_site_id}-[a-zA-Z0-9]+\.webp'
    match = re.search(pattern, response.text)

    if match:
        poster_url = match.group(0)
        return poster_url, movie_id

    return None


def set_movie_poster(movie_id: str, poster_url: str) -> None:
    """
    UPDATE movies_movie table
    SET poster_url for record

    Args:
        poster_url: str
        movie_id: str

    Returns:
        None
    """

    sql_command = """
        UPDATE movies_movie
        SET poster_url = %s
        WHERE id = %s
        """
    
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (poster_url, movie_id))
    conx.commit()
    conx.close()



if __name__ == '__main__':
    movies = get_movies_from_db()

    for movie in movies:
        movie_poster, movie_id = get_movie_poster_url(movie)
        if movie_poster:
            set_movie_poster(movie_id, movie_poster)
        else:
            continue
