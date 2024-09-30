import os
import re
import time
import aiohttp
import requests
import mysql.connector
from typing import List, Dict
from mysql.connector import errorcode
from constants import (
    SUBTITLE_URL,
    ENGLISH_PREFIX,
    PERSIAN_PREFIX,
    BASE_URL,
    MOVIE_INFO_URL,
)
from utils import find_movie_quality, find_series_season, get_last_movie_id



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


def create_user_record(data: tuple) -> int:
    """
    Creating User record
    get user info from start command and populate database

    Args:
        data: tuple (user info)
    
    Returns:
        int: last row ID
    """

    sql_command = """
            INSERT INTO movies_user (
                telegram_id, username, first_name, last_name, created_at, last_use
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """
    try:
        cnx = connect_to_database()
        cursor = cnx.cursor()
        cursor.execute(sql_command, data)
        cnx.commit()
        cursor.close()
        cnx.close()
        return cursor.lastrowid
    
    except mysql.connector.Error as err:
        print(f'Something failed: {err}')


def create_user_search_record(data: tuple) -> None:
    """
    Creating User searcg record
    get user search detail from inline-query search and populate database

    Args:
        data: tuple (user search info)
    
    Returns:
        None
    """

    sql_command = """
            INSERT INTO movies_usersearch (
                query, timestamp, user_id
            )
            VALUES (%s, %s, %s)
            """
    try:
        cnx = connect_to_database()
        cursor = cnx.cursor()
        cursor.execute(sql_command, data)
        cnx.commit()
        cursor.close()
        cnx.close()
    
    except mysql.connector.Error as err:
        print(f'Something failed: {err}')


def remove_user_from_db(telegram_id: str, user_database_id: str) -> None:
    """
    Delete Both User and User-Records of Someone Who Blocks Bot.

    Args:
        telegram_id: str
        user_database_id: str
    
    Returns:
        None
    """

    sql_command_user_search = """ DELETE FROM movies_usersearch WHERE user_id = %s """
    sql_command_user = """ DELETE FROM movies_user WHERE telegram_id = %s """

    try:
        cnx = connect_to_database()
        cursor = cnx.cursor()
        cursor.execute(sql_command_user_search, (user_database_id, ))
        cursor.execute(sql_command_user, (telegram_id, ))
        cnx.commit()
        cursor.close()
        cnx.close()
    
    except mysql.connector.Error as err:
        print(f'Something failed: {err}')


def get_movie_imdb_info(movie: str, api_key: str) -> Dict:
    response = requests.get(f'{MOVIE_INFO_URL}/?t={movie}&apikey={api_key}')
    return response.json()


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
        has_published_at: bool -> (default=False)

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
    movie_site_id = movie_url.split('/')[3]
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(movie_url, headers=headers)
    pattern = rf'{BASE_URL}/wp-content/uploads/poster/.*/{movie_site_id}-[a-zA-Z0-9]+\.webp'
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


def get_movie_data(record: tuple) -> bool:
    """
    Get a single arg as record
    request the given url, seprate mkv|mp4 file extensions with regex
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
    request the given url, seprate season url with regex
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
    
    sql_command = """ SELECT * FROM movies_movie WHERE trending = 1 """
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


def get_user_from_db_by_telegram_id(telegram_id: str) -> tuple | None:
    """
    Read User information by TelegramID

    Returns:
        Tuple | None
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


def update_user_last_use(datetime_info: str, user_id: int) -> None:
    """
    Update last_use field of User Record based on ID of user in database
    Whenever User Search in Bot or Start the Bot.

    Args:
        datetime_info: strftime
        user_id: int

    Returns:
        None
    """

    sql_command = f"""
            UPDATE movies_user
            SET last_use = %s
            WHERE id = %s
            """
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (datetime_info, user_id))
    conx.commit()
    cursor.close()
    conx.close()


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


async def movie_links_endpoint(movie_id: int) -> dict:
    """
    Get a single arg as name
    send a request to specified endpoint and set name parameter as query_string
    
    Args:
        movie_id: int

    Returns:
        Dict
    """
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://127.0.0.1:8000/api/links/?movie_id={movie_id}') as response:
            return await response.json()