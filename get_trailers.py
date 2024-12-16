import time
import sys
from utils import get_datetime_info
from dal import get_movies_from_db, get_movie_trailer_url, set_movie_trailer, get_movie_from_db_by_id



def main():
    datetime_info = get_datetime_info()

    year = datetime_info.get('year')
    month = datetime_info.get('month')
    day = datetime_info.get('day')
    hour = datetime_info.get('hour')
    minute = datetime_info.get('minute')
    second = datetime_info.get('second')

    if len(sys.argv) > 1:
        movie_id = sys.argv[1]
        movie = get_movie_from_db_by_id(movie_id)
        movie_info = get_movie_trailer_url(movie)
        if movie_info:
            movie_trailer = movie_info[0]
            movie_id = movie_info[1]
            print(f'++ Manually Runned ++\Trailer for movie with id: {movie_id} -> Trailer {movie_trailer}\nExtracted On: {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')
            set_movie_trailer(movie_id, movie_trailer)

    else:
        movies = get_movies_from_db()
        movie_counts = 0
        for movie in movies:
            movie_info = get_movie_trailer_url(movie)
            if movie_info:
                movie_trailer = movie_info[0]
                movie_id = movie_info[1]
                set_movie_trailer(movie_id, movie_trailer)
                movie_counts += 1
                time.sleep(2)
            else:
                continue

        print(f'Trailers for {movie_counts} Movies\nExtracted On: {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')


if __name__ == '__main__':
    main()
