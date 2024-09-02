from dal import get_movie_data, get_series_data, get_movie_from_db_by_id


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
    return



if __name__ == '__main__':
    row_id = input('Movie ID to Extract Download Links: ')
    movies = extract_movie_links(row_id)