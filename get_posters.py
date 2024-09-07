import time
import sys
from datetime import datetime
from dal import get_movies_from_db, get_movie_poster_url, set_movie_poster, get_movie_from_db_by_id



datetime_info = datetime.now()
year = datetime_info.year
month = datetime_info.month
day = datetime_info.day
hour = datetime_info.hour
minute = datetime_info.minute
second = datetime_info.second

if len(sys.argv) > 1:
    movie_id = sys.argv[1]
    movie = get_movie_from_db_by_id(movie_id)
    movie_info = get_movie_poster_url(movie)
    if movie_info:
        movie_poster = movie_info[0]
        movie_id = movie_info[1]
        print(f'++ Manually Runned ++\nPoster for movie with id: {movie_id} -> Poster{movie_poster}\nExtracted On: {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')
        set_movie_poster(movie_id, movie_poster)

else:
    movies = get_movies_from_db()

    for movie in movies:
        movie_info = get_movie_poster_url(movie)
        if movie_info:
            movie_poster = movie_info[0]
            movie_id = movie_info[1]
            print(f'Poster for movie with id: {movie_id} -> Poster {movie_poster}\nExtracted On: {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')
            set_movie_poster(movie_id, movie_poster)
            time.sleep(2)
        else:
            continue
