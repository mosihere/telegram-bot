import sys
import time
from utils import get_datetime_info
from dal import get_movies_from_db, get_movie_from_db_by_id, get_movie_subtitle, set_movie_subtitle




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
        movie_info = get_movie_subtitle(movie)
        if movie_info:
            movie_subtitle = movie_info[0]
            movie_id = movie_info[1]
            print(f'++ Manually Runned ++\nSubtitle for movie with id: {movie_id} -> Subtitle{movie_subtitle}\nExtracted On: {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')
            set_movie_subtitle(subtitle_url= movie_subtitle, movie_id=movie_id)

    else:
        movies = get_movies_from_db()
        movie_counts = 0
        for movie in movies:
            movie_info = get_movie_subtitle(movie)
            if movie_info:
                movie_subtitle = movie_info[0]
                movie_id = movie_info[1]
                set_movie_subtitle(subtitle_url=movie_subtitle, movie_id=movie_id)
                movie_counts += 1
                time.sleep(2)
            else:
                continue

        print(f'Subtitle for {movie_counts} Movies\nExtracted On: {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')


if __name__ == '__main__':
    main()