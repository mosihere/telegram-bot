import os
import re
import time
import requests
import mysql.connector
from typing import List, Dict
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
        return 'SomeThing failed.'


def create_record_for_movies(val: list, has_published_date = False):

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
    try:
        print(val)
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


def get_movie_data(record: tuple):
    id = record[0]
    url = record[2]
    print(url)
    response = requests.get(url)
    links = re.findall(r'https://.*kingupload.*mkv', response.text)

    for link in links:
        quality = find_movie_quality(link)
        if not quality:
            continue
        quality = quality[0]
        codec = 'x265' if 'x265' in link else 'x264'
        data = (link, quality, id, codec)
        create_record_for_movie_links(data)
        time.sleep(2)


def get_series_data(record: tuple):
    id = record[0]
    url = record[2]
    print(url)
    response = requests.get(url)
    links_page = re.findall(r'https://.*kingupload.*/Serial/.*[0-9]/', response.text)
    for link in links_page:
        season = find_series_season(link)
        if not season:
            continue
        season = season[0]
        codec = 'x265' if 'x265' in link else 'x264'
        data = (link, season, id, codec)
        create_record_for_movie_links(data)
        time.sleep(2)


def movie_data_normalizer(movies: List[Dict]) -> list:
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

    quality = re.findall(r'[0-9]{3,4}[p]',link)

    return quality


def find_series_season(link: list):
   
   season = re.findall(r'S\d{2}', link)

   return season


def get_movies_from_db():
    sql_command = """ SELECT * FROM movies_movie WHERE id > 460"""
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command)
    movies = cursor.fetchall()
    return movies


def movie_endpoint(name: str):
    response = requests.get(f'http://127.0.0.1:8000/movies/links/?movie_name={name}')
    return response.json()





if __name__ == '__main__':
    movies = get_movies_from_db()
    for movie in movies:
        links = get_movie_data(movie)
        print(links)
