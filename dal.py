import os
import re
import requests
import mysql.connector
from mysql.connector import errorcode



def connect_to_database():

    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.environ['DB_PASS'],
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



def is_duplicate(movie_name):
    
    sql = """ SELECT * FROM movies WHERE name=%s """

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
        return 'SomeThing failed.'


def create_record(val: list, has_published_date = False):

    if has_published_date:
       try:
            sql_command = """
                INSERT INTO movies (
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
            INSERT INTO movies (
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


def read_record(movie_name: str) -> None:
   
    sql_command = """SELECT * FROM movies WHERE name LIKE %s """

    in_between_param = ("%" + movie_name + "%")
    start_with_param = (movie_name + "%")
    cnx = connect_to_database()
    cursor = cnx.cursor()

    cursor.execute(sql_command, (start_with_param, ))
    movies = cursor.fetchall()

    if movies:
        cnx.close()
        return movies
    
    else:
        cursor.execute(sql_command, (in_between_param, ))
        movies = cursor.fetchall()
        cnx.close()
        return movies


def get_links(records: list):

    for element in records:
        url = element[1]
        movie_name = element[2]
        response = requests.get(url)
        links = re.findall(r'https://.*kingupload.*mkv', response.text)
        links_page = re.findall(r'https://.*kingupload.*[0-9]/', response.text)

        qualities = find_movie_quality(links)
        get_seasons = find_series_season(links_page)

        if links and links_page and get_seasons and qualities:
            sorted_season = sorted(list(set(get_seasons)))
            sorted_links_page = sorted(list(set(links_page)))
            
            return links, movie_name, qualities, sorted_links_page, sorted_season
        
        elif links or links_page and not get_seasons:
            return links, movie_name, qualities
        
        elif links_page and not links:
            return links_page, movie_name, get_seasons
        
        else:
           return ''


def find_movie_quality(links: list) -> None:

    quality = re.findall(r'[0-9]{3,4}[p]', ' '.join(links))

    return quality


def find_series_season(links: list):
   
   season = re.findall(r'S\d{2}', ' '.join(links))

   return season