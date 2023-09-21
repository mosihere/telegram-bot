import os
import re
import requests
import mysql.connector
from mysql.connector import errorcode




try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ['DB_PASS'],
        database="movie"
)

  
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with your user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)

def is_duplicate(movie_name):
    sql = """ SELECT * FROM movies WHERE name=%s """

    cursor = db.cursor()
    try:
        cursor.execute(sql, (movie_name, ))
        movie = cursor.fetchone()
        # print(movie)
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
        
        cursor = db.cursor()
        cursor.executemany(sql_command, val)
        db.commit()

       except mysql.connector.Error as err:
           print('Duplicate Entries Found!')
           pass
          
    else:
        try:
            sql_command = """
            INSERT INTO movies (
                url, name
            )
            VALUES (%s, %s) """
        
            cursor = db.cursor()
            cursor.executemany(sql_command, val)
            db.commit()
        
        except mysql.connector.Error as err:
           print('Duplicate Entries Found!')
           pass
        

def read_record(movie_name: str) -> None:
   
    sql_command = """SELECT * FROM movies WHERE name LIKE %s """

    in_between_param = ("%" + movie_name + "%")
    start_with_param = (movie_name + "%")
    cursor = db.cursor()

    cursor.execute(sql_command, (start_with_param, ))
    movies = cursor.fetchall()

    if movies:
        return movies
    
    else:
        cursor.execute(sql_command, (in_between_param, ))
        movies = cursor.fetchall()
        return movies


def get_links(records: list):

    for element in records:
        url = element[1]
        movie_name = element[2]
        response = requests.get(url)
        links = re.findall(r'https://.*kingupload.*mkv', response.text)
        qualites = find_movie_quality(links)

        if links:
            return links, movie_name, qualites
        
        else:
            new_links = re.findall(r'https://.*kingupload.*', response.text)
            qualites = find_movie_quality(new_links)

            return new_links, movie_name, qualites
    

def find_movie_quality(links: list) -> None:

    quality = re.findall(r'[0-9]{3,4}[p]', ' '.join(links))

    return quality
