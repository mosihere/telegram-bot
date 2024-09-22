import time
from dal import get_movies_from_db, get_movie_subtitle, set_movie_subtitle






if __name__ == '__main__':
    movies = get_movies_from_db()
    movie_counts = 0
    for movie in movies:
        movie_info = get_movie_subtitle(movie)
        if movie_info:
            movie_subtitle = movie_info[0]
            movie_id = movie_info[1]
            set_movie_subtitle(movie_subtitle, movie_id)
            movie_counts += 1
            time.sleep(2)
        else:
            continue
