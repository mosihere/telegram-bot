import re
import time
import aiohttp
import requests
import mysql.connector
from decouple import config
from typing import List, Dict
from mysql.connector import errorcode
from constants import (
    SUBTITLE_URL,
    ENGLISH_PREFIX,
    PERSIAN_PREFIX,
    BASE_URL,
    MOVIE_INFO_URL,
)
from utils import find_movie_quality, find_series_season, get_last_movie_id, make_request



def connect_to_database():
    """
    Connecting to Database

    Returns:
        MySQL-connection
    """

    try:
        db = mysql.connector.connect(
            host=config('DB_HOST'),
            user=config('DB_USER'),
            password=config('DB_PASS'),
            database=config('DB')
    )
        return db
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return "Something is wrong with your user name or password"

        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            return "Database does not exist"

        else:
            return err


async def create_user_record(payload: dict) -> dict:
    """
    Creating User record
    get user info from start command and send a POST request to users endpoint

    Args:
        payload: dict (user info)
    
    Returns:
        dict: created_user_record
    """

    response = await make_request('http://127.0.0.1:8000/api/users/', method='POST', payload=payload)

    if 'error' in response:
        print("Error creating user record:", response['error'])

    return response


async def create_user_search_record(payload: Dict) -> Dict:
    """
    Creating User search record
    get user search detail from inline-query search
    send a POST request to the endpoint to create user-search record.

    Args:
        payload: dict (user search info)
    
    Returns:
        dict
    """

    response = await make_request('http://127.0.0.1:8000/api/user-searches/', method='POST', payload=payload)

    if 'error' in response:
        print("Error creating user search record:", response['error'])

    return response


async def remove_user_from_db(user_database_id: str) -> dict:
    """
    Delete Both User and User-Records of Someone Who Blocks Bot.

    Args:
        user_database_id: str
    
    Returns:
        dict
    """

    response = await make_request(f'http://127.0.0.1:8000/api/users/{user_database_id}', method='DELETE')

    if 'error' in response:
        print("Error deleting user:", response['error'])

    return response


async def get_movie_imdb_info(movie: str, api_key: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{MOVIE_INFO_URL}/?t={movie}&apikey={api_key}') as response:
            return await response.json()


def is_duplicate(movie_name: str) -> bool | str:
    """
    Get a single arg as movie_name, query the name that movie
    if exists and return an id:
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
        return f'Something failed: {err}'


def create_record_for_movies(val: list[tuple], has_published_date: bool = False) -> int | str:
    """
    Get two args as val and has_published_date
    if has_published_date:
        create record in db with populating published_at field
    else:
        create record without populating published_at field
    
    Args:
        val: list
        has_published_date: bool -> (default=False)

    Returns:
        int | str(Error)
    """

    if has_published_date:
        sql_command = """
            INSERT INTO movies_movie (
                url, name, published_at
            )
            VALUES (%s, %s, %s)
            """
    else:
        sql_command = """
        INSERT INTO movies_movie (
            url, name
        )
        VALUES (%s, %s)
        """

    try:
        cnx = connect_to_database()
        cursor = cnx.cursor()
        cursor.executemany(sql_command, val)
        inserted_rows = cursor.rowcount
        cnx.commit()
        cnx.close()
        return inserted_rows if inserted_rows > 0 else 0
        
    except mysql.connector.Error as err:
        return f'We faced an error: {err}'


def create_record_for_movie_links(records: List[tuple]) -> int | str:
    """
    Get a single arg as records
    try to insert a list of records to database with specified query and return lastrowid
    in case of exception returns error message as string.

    Args:
        records: List[tuple]

    Returns:
        int | str(Error)
    """

    try:
        sql_command = """
            INSERT IGNORE INTO movies_link (
                link, quality, movie_id, codec
            )
            VALUES (%s, %s, %s, %s) """
        cnx = connect_to_database()
        cursor = cnx.cursor()
        cursor.executemany(sql_command, records)
        inserted_rows = cursor.rowcount
        cnx.commit()
        cnx.close()
        return inserted_rows
    
    except mysql.connector.Error as err:
        return f'We faced an error: {err}'


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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(movie_url, headers=headers)
    pattern = rf'{BASE_URL}/wp-content/uploads/\d{{4}}/\d{{2}}/[a-zA-Z0-9-]+\.jpg'
    match = re.search(pattern, response.text)

    if match:
        poster_url = match.group(0)
        return poster_url, movie_id

    return None


def get_movie_subtitle(record: tuple) -> tuple | None:
    """
    Get a single argument as record
    Unpack result and assign them to variables
    send a get request to given URL
    find movie subtitle
    return that subtitle_url

    Args:
        record: tuple
    
    Returns:
        tuple(str, str) | None
    """
    movie_id = record[0]
    movie_title = record[1]
    url = fr'{SUBTITLE_URL}{ENGLISH_PREFIX}{movie_title}'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    session = requests.Session()
    response = session.get(f'{url}', headers=headers)
    pattern = r'https:\/\/dl\.subtitlestar\.com\/dlsub\/[a-zA-Z0-9-]+-[a-zA-Z0-9-]+\.zip'
    match = re.search(pattern, response.text)

    if match:
        return match.group(0), movie_id
    else:
        time.sleep(1.5)
        url = fr'{SUBTITLE_URL}{PERSIAN_PREFIX}{movie_title}'
        response = session.get(f'{url}', headers=headers)
        match = re.search(pattern, response.text)
        if match:
            return match.group(0), movie_id
        else:
            return None


def get_movie_trailer_url(record: tuple) -> tuple | None:
    """
    Get a single argument as record
    Unpack result and assign them to variables
    send a get request to given URL
    find movie poster
    return that trailer_url

    Args:
        record: tuple
    
    Returns:
        tuple(str, str) | None
    """

    movie_id = record[0]
    movie_url = record[2]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(movie_url, headers=headers)
    pattern = r'https?://[^ ]*trailer[^ ]*\.mp4'
    match = re.search(pattern, response.text, re.IGNORECASE)

    if match:
        poster_url = match.group(0)
        return poster_url, movie_id

    return None
        

def set_movie_subtitle(subtitle_url: str, movie_id: str) -> None:
    """
    UPDATE movies_movie table
    SET subtitle_url for record

    Args:
        subtitle_url: str
        movie_id: str

    Returns:
        None
    """

    sql_command = """
            UPDATE movies_movie
            SET subtitle_url = %s
            WHERE id = %s
            """
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (subtitle_url, movie_id))
    conx.commit()
    conx.close()


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


def set_movie_trailer(movie_id: str, trailer_url: str) -> None:
    """
    UPDATE movies_movie table
    SET trailer_url for record

    Args:
        trailer_url: str
        movie_id: str

    Returns:
        None
    """

    sql_command = """
        UPDATE movies_movie
        SET trailer_url = %s
        WHERE id = %s
        """
    
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (trailer_url, movie_id))
    conx.commit()
    conx.close()


def get_movie_data(record: tuple) -> bool:
    """
    Get a single arg as record
    request the given url, separate mkv|mp4 file extensions with regex
    iterate on founded direct mkv|mp4 links to find quality of them
    and then creating a movie_record.
    
    Args:
        record: tuple

    Returns:
        bool
    """

    id = record[0]
    url = record[2]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    links = re.findall(r'https://.*kingupload.*(?:mp4|mkv)', response.text)
    records_to_insert = list()

    if not links:
        return False
    
    links = list(set(links))
    for link in links:
        quality = find_movie_quality(link)
        if not quality:
            continue
        quality = quality[0]
        codec = 'x265' if 'x265' in link else 'x264'
        data = (link, quality, id, codec)
        records_to_insert.append(data)
        time.sleep(2)
    create_record_for_movie_links(records_to_insert)
    return True


def get_series_data(record: tuple) -> None:
    """
    Get a single arg as record
    request the given url, separate season url with regex
    iterate on founded direct seasons links to find season number
    and then creating a movie_record.
    
    Args:
        record: tuple

    Returns:
        None
    """

    id = record[0]
    url = record[2]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    links_page = re.findall(r'https://.*kingupload.*/Serial/.*[0-9]/', response.text)
    new_links_page = re.findall(r'https://.*kingupload.*/Series/.*[0-9]/', response.text)
    records_to_insert = list()

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
            records_to_insert.append(data)
            time.sleep(2)
        create_record_for_movie_links(records_to_insert)
            
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
            records_to_insert.append(data)
            time.sleep(2)
        create_record_for_movie_links(records_to_insert)


def get_movies_from_db() -> List[tuple]:
    """
    Read records from Database 

    Returns:
        list(tuple)
    """

    last_row_id = get_last_movie_id()
    sql_command = f""" SELECT * FROM movies_movie WHERE id > %s"""
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (last_row_id,))
    movies = cursor.fetchall()
    conx.close()
    return movies


def get_movie_from_db_by_id(movie_id: str) -> tuple | None:
    """
    Read Movie information by ID

    Args:
        movie_id: str

    Returns:
        Tuple | None
    """

    sql_command = f""" SELECT * FROM movies_movie WHERE id = %s"""
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    conx.close()
    return movie



def clear_trending_movie() -> int:
    """ 
    Clear All marks from Movies
    Before Mark new Movies as trending

    Returns:
        row_count: int (Number of Updated Rows)
    """

    sql_command = """ UPDATE movies_movie SET trending = 0 WHERE trending = 1 """
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command)
    updated_rows = cursor.rowcount
    conx.commit()
    cursor.close()
    conx.close()
    return updated_rows


def mark_trending_movie(movie_title: str) -> int:
    """
    Get a movie title and Check if that movie exists in Database
    Mark that Movie as Trending.

    Args:
        movie_title: str

    Returns:
        row_count: int (Number of Updated Rows)
    """

    movie_title = f"%{movie_title}%"
    sql_command = f""" UPDATE movies_movie SET trending = 1 where name LIKE %s """
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (movie_title,))
    updated_rows = cursor.rowcount
    conx.commit()
    cursor.close()
    conx.close()
    return updated_rows


def get_trending_movies(authorization: str) -> dict:
    """
    Get Trends Movies From Third-Party API.

    Args:
        authorization: str(Token)
    
    Returns:
        Dict
    """

    url = "https://api.themoviedb.org/3/trending/movie/week?language=en-US"

    headers = {
        "accept": "application/json",
        "Authorization": authorization
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()['results']
    else:
        return {"error": "Unable to fetch trending movies"}


def suggest_trending_movies() -> List[tuple] | None:
    """
    Select all trends movies from Database

    Returns:
        List(Tuple): Movie Records | None
    """
    
    sql_command = """ SELECT id, name FROM movies_movie WHERE trending = 1 """
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command)
    movies = cursor.fetchall()
    cursor.close()
    conx.close()
    return movies


def get_all_users_telegram_ids() -> List[tuple] | None:
    """
    Get Users TelegramID

    Returns:
        List[Tuple]: Users Info | None
    """

    sql_command = """ SELECT telegram_id, id FROM movies_user """
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command)
    users = cursor.fetchall()
    cursor.close()
    conx.close()
    return users


def get_user_from_db_by_telegram_id(telegram_id: int) -> int | None:
    """
    Read User information by TelegramID

    Returns:
        int | None
    """

    sql_command = f""" SELECT id FROM movies_user WHERE telegram_id = %s"""
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (telegram_id, ))
    user = cursor.fetchone()
    cursor.close()
    conx.close()
    if user:
        return user[0]
    
    return None


async def update_user_last_use(datetime_info: str, username: str, first_name: str, last_name: str, user_id: int) -> dict:
    """
    Update last_use field of User based on ID of the user
    Whenever User Search in Bot or Start the Bot.

    Args:
        datetime_info: strftime
        user_id: int

    Returns:
        dict: (Updated Record)
    """

    payload = {
        'last_use': datetime_info,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        }
    response = await make_request(f'http://127.0.0.1:8000/api/users/{user_id}/', method='PATCH', payload=payload)
    return response


async def movie_endpoint(name: str, telegram_id: int) -> List[dict]:
    """
    Get a single arg as name
    send a request to specified endpoint and set name parameter as query_string
    
    Args:
        name: str
        telegram_id: int

    Returns:
        Dict
    """

    headers = {}
    if telegram_id:
        headers['X-Telegram-User-ID'] = str(telegram_id)

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'http://127.0.0.1:8000/api/movies/?search={name}') as response:
            if response.status == 429:
                return [{"id": "rate_limit", "name": "Rate limit exceeded. Please try again later.", "description": ""}]
            
            return await response.json()


async def movie_links_endpoint(movie_id: str, telegram_id: int = None) -> list[dict]:
    """
    Get a single arg as name
    send a request to specified endpoint and set name parameter as query_string
    
    Args:
        movie_id: str
        telegram_id: int

    Returns:
        Dict
    """

    headers = {}
    if telegram_id:
        headers['X-Telegram-User-ID'] = str(telegram_id)

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f'http://127.0.0.1:8000/api/links/?movie_id={movie_id}') as response:
            return await response.json()