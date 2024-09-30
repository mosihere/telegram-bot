import sys
from utils import get_datetime_info, update_last_movie_id
from dal import get_movie_data, get_series_data, get_movie_from_db_by_id, get_movies_from_db



def extract_movie_links(movie_id: str) -> None:
    """
    Extract download links for the movie or series with the given ID.
    
    Args:
        movie_id (str): The ID of the movie to process.
    """

    movie = get_movie_from_db_by_id(movie_id)

    if not movie:
        print("No movie found with the given ID.")
        return
    
    get_movie_data(movie)
    get_series_data(movie)


datetime_info = get_datetime_info()

year = datetime_info.get('year')
month = datetime_info.get('month')
day = datetime_info.get('day')
hour = datetime_info.get('hour')
minute = datetime_info.get('minute')
second = datetime_info.get('second')


if __name__ == '__main__':

    if len(sys.argv) > 1:
        movie_id = sys.argv[1]
        extract_movie_links(movie_id)
        print(f'Links of Movie {movie_id} Extracted On {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')

    else:
        movies = get_movies_from_db()
        if movies:
            for movie in movies:
                series_links = get_series_data(movie)
                movie_links = get_movie_data(movie)
            try:
                update_last_movie_id(movies[-1][0])
            except IndexError:
                pass
            print(f'{len(movies)} Movies/Series Links Extracted On: {year:04d}-{month:02d}-{day:02d}\nTime: {hour:02d}:{minute:02d}:{second:02d}\n')

        else:
            print('No movies found to process.')