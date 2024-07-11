import os
import re
import time
import aiohttp
import requests
import mysql.connector
from tabulate import tabulate
from typing import List, Dict
from mysql.connector import errorcode


MOVIE_INFO_URL = 'https://www.omdbapi.com'


def connect_to_database():
    """
    Connecting to Database
    
    Args:
        None

    Returns:
        MySQL-connection
    """

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.environ.get('DB_PASS'),
            database="movie"
    )
        return db
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Something is wrong with your user name or password"

        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return "Database does not exist"

        else:
            return err


def user_data_log(data: tuple) -> bool:
    """
    Append user data in a logfile named: user_data.log
    """

    try:
        with open('user_data.log', 'a') as file:
            file.write(f'{data}\n')
            return True
        
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")
        return False


def get_movie_imdb_info(movie: str, api_key: str) -> Dict:
    response = requests.get(f'{MOVIE_INFO_URL}/?t={movie}&apikey={api_key}')
    return response.json()


def normalized_imdb_info(movie_info: dict):
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


def is_duplicate(movie_name: str) -> bool | str:
    """
    Get a single arg as movie_name, query the name that movie
    if exists and return a id:
        return True
    else:
        return False
    
    Args:
        movie_name: str

    Returns:
        bool | str(Error)
    """
    
    sql = """ SELECT id FROM movies_movie WHERE name=%s """

    try:
        cnx = connect_to_database()
        cursor = cnx.cursor()
        cursor.execute(sql, (movie_name, ))
        movie = cursor.fetchone()
        cnx.close()
        if movie:
            return True
        
        return False
    
    except mysql.connector.Error as err:
        return f'SomeThing failed: {err}'


def create_record_for_movies(val: list[tuple], has_published_date: bool = False) -> None | str:
    """
    Get two args as val and has_published_date
    if has_published_date:
        create record in db with populating published_at field
    else:
        create record without populating published_at field
    
    Args:
        val: list
        has_published_at: bool -> (default=False)

    Returns:
        None | str(Error)
    """

    if has_published_date:
       try:
            sql_command = """
                INSERT INTO movies_movie (
                    url, name, published_at
                )
                VALUES (%s, %s, %s) """
            cnx = connect_to_database()
            cursor = cnx.cursor()
            cursor.executemany(sql_command, val)
            cnx.commit()
            cnx.close()

       except mysql.connector.Error as err:
           return f'We faced an error: {err}'
          
    else:
        try:
            sql_command = """
            INSERT INTO movies_movie (
                url, name
            )
            VALUES (%s, %s) """
        
            cnx = connect_to_database()
            cursor = cnx.cursor()
            cursor.executemany(sql_command, val)
            cnx.commit()
            cnx.close()
        
        except mysql.connector.Error as err:
           return f'We faced an error: {err}'


def create_record_for_movie_links(val: tuple) -> int | str:
    """
    Get a single arg as val
    try to insert a value to database with specified query and return lastrowid
    in case of exception returns error message as string.

    Args:
        val: tuple

    Returns:
        int | str(Error)
    """

    tabular_titles = ['Link', 'Quality / Season', 'ID', 'Codec']

    try:
        print(tabulate(tabular_data=[tabular_titles, val]))
        print()
        sql_command = """
            INSERT INTO movies_link (
                link, quality, movie_id, codec
            )
            VALUES (%s, %s, %s, %s) """
        cnx = connect_to_database()
        cursor = cnx.cursor()
        cursor.execute(sql_command, val)
        cnx.commit()
        cnx.close()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        return f'We faced an error: {err}'


def get_movie_data(record: tuple) -> None:
    """
    Get a single arg as record
    request the given url, seprate mkv file extensions with regex
    iterate on finded direct mkv links to find quality of them
    and then creating a movie_record.
    
    Args:
        record: tuple

    Returns:
        None
    """

    id = record[0]
    url = record[2]
    print('\n++ Extracted Movie URLs ++\n')
    response = requests.get(url)
    links = re.findall(r'https://.*kingupload.*mkv', response.text)
    if links:
        links = list(set(links))
        for link in links:
            quality = find_movie_quality(link)
            if not quality:
                continue
            quality = quality[0]
            codec = 'x265' if 'x265' in link else 'x264'
            data = (link, quality, id, codec)
            create_record_for_movie_links(data)
            time.sleep(2)
        else:
            return True
    else:
        return False


def get_series_data(record: tuple):
    """
    Get a single arg as record
    request the given url, seprate season url with regex
    iterate on finded direct seasons links to find season number
    and then creating a movie_record.
    
    Args:
        record: tuple

    Returns:
        None
    """

    id = record[0]
    url = record[2]
    print('\n++ Extracted Series URLs ++\n')
    response = requests.get(url)
    links_page = re.findall(r'https://.*kingupload.*/Serial/.*[0-9]/', response.text)
    new_links_page = re.findall(r'https://.*kingupload.*/Series/.*[0-9]/', response.text)

    if links_page:
        links_page = list(set(links_page))
        for link in links_page:
            serial_link = re.search(r'https://.*kingupload.*/Serial/.*/S[0-9]{2}/', link)
            if not serial_link:
                continue
            serial_link = serial_link.group(0)
            season = find_series_season(serial_link)
            if not season:
                continue
            season = season[0]
            codec = 'x265' if 'x265' in serial_link else 'x264'
            data = (serial_link, season, id, codec)
            create_record_for_movie_links(data)
            time.sleep(2)
            
    elif new_links_page:
        new_links_page = list(set(new_links_page))
        for link in new_links_page:
            series_link = re.search(r'https://.*kingupload.*/Series/.*/S[0-9]{2}/', link)
            if not series_link:
                continue
            series_link = series_link.group(0)
            season = find_series_season(series_link)
            if not season:
                continue
            season = season[0]
            codec = 'x265' if 'x265' in series_link else 'x264'
            data = (series_link, season, id, codec)
            create_record_for_movie_links(data)
            time.sleep(2)
    else:
        return


def movie_data_normalizer(movies: List[Dict]) -> List[Dict]:
    """
    Get a single arg as movies
    iterate on the given list
    create a dictionary for each object
    get neccessary data and append them to a new list
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
            'name': movie.get('movie').get('name'),
            'published_at': movie.get('movie').get('published_at'),
            }
        data.append(movie_info)

    return data


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


def get_movies_from_db() -> List[tuple]:
    """
    Read records from Database 

    Returns:
        list(tuple)
    """

    sql_command = """ SELECT * FROM movies_movie WHERE id = 3857"""
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command)
    movies = cursor.fetchall()
    return movies


async def movie_endpoint(name: str) -> dict:
    """
    Get a single arg as name
    send a request to specified endpoint and set name parameter as query_string
    
    Args:
        name: str

    Returns:
        Dict
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://127.0.0.1:8000/api/movies/?search={name}') as response:
            return await response.json()


def movie_links_endpoint(movie_id: int) -> dict:
    """
    Get a single arg as name
    send a request to specified endpoint and set name parameter as query_string
    
    Args:
        name: str

    Returns:
        Dict
    """

    response = requests.get(f'http://127.0.0.1:8000/api/links/?movie_id={movie_id}')
    return response.json()





if __name__ == '__main__':
    movies = get_movies_from_db()
    for movie in movies:
        series_links = get_series_data(movie)
        movie_links = get_movie_data(movie)