from typing import List
from dal import get_movie_data, get_series_data, connect_to_database


def get_movies_from_db(row_id: str) -> List[tuple]:
    """
    Read record from Database 

    Returns:
        list(tuple)
    """

    sql_command = f""" SELECT * FROM movies_movie WHERE id = %s"""
    conx = connect_to_database()
    cursor = conx.cursor()
    cursor.execute(sql_command, (row_id,))
    movies = cursor.fetchall()
    conx.close()
    return movies



if __name__ == '__main__':
    row_id = input('Movie ID to Extract Download Links: ')
    movies = get_movies_from_db(row_id)
    for movie in movies:
            series_links = get_series_data(movie)
            movie_links = get_movie_data(movie)