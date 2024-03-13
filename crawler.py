import re
import time
import datetime
import requests
from dal import is_duplicate, create_record_for_movies


# Careful! Just run this module when you want crawl movies.


BASE_URL = "https://www.f2m45.fun"



def movie_crawler(start_page: int, end_page: int) -> list:
    """
    Get two args as start_page and end_page, send a get request to the base url
    then with regex find all movie_links
    
    Args:
        start_page: int
        end_page: int

    Returns:
        list(str)
    """

    data = list()

    for page in range(start_page, end_page + 1):

        response = requests.get(f'{BASE_URL}/page/{page}')

        time.sleep(2)

        links = re.findall(f'{BASE_URL}/\d*/\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*', response.text)
        data.append(list(set(links)))
        
    return data


def series_crawler(start_page: int, end_page: int) -> list:
    """
    Get two args as start_page and end_page, send a get request to the base url
    then with regex find all series_link
    
    Args:
        start_page: int
        end_page: int

    Returns:
        list(str)
    """

    data = list()

    for page in range(start_page, end_page + 1):

        response = requests.get(f'{BASE_URL}/category/دانلود-سریال/page/{page}')

        time.sleep(2)

        links = re.findall(f'{BASE_URL}/\d*/\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*', response.text)
        data.append(list(set(links)))
        
    return data



def remove_duplicate(movie_list: list) -> list:
    """
    Get a single arg as movie_list, iterate on each movie and append them to new list
    finally we create a list of set to remove duplicate movies-series.    
    Args:
        movie_list: list

    Returns:
        list(str)
    """
    
    new_list = list()

    for part in movie_list:
        for movie in part:
            new_list.append(movie)

    normalized_data = list(set(new_list))

    return normalized_data


def ready_for_insert(movies: list) -> tuple:
    """
    Get a single arg as movies(url of movies), iterate on them
    get_data from urls --> movie_name, published_date ...
    call is_duplicate function for each movie to check is that exists in db or not!
    then check if there is a date in url or not, and finally call create_record_for_movies() function
    return duplicate_movies count and new_movies crawled.
    
    Args:
        movies: list

    Returns:
        tuple(duplicate_counter: int, crawled_data: int)
    """

    duplicate_counter = 0
    movies_data = list()
    movies_with_published_date = list()

    for data in movies:

        url = data
        movie_name = data.split('/')
        movie_name = movie_name[-1]

        if is_duplicate(movie_name):
            duplicate_counter += 1
            continue
 
        published_date:str = movie_name.split('-')
        published_date = published_date[-1]

        if published_date.isnumeric() and len(published_date) == 4:
            info = (url, movie_name, published_date)
            movies_with_published_date.append(info)

        else:
            data = (url, movie_name)
            movies_data.append(data)

    crawled_counter = len(movies_data) + len(movies_with_published_date)

    create_record_for_movies(movies_data)
    create_record_for_movies(movies_with_published_date, has_published_date=True)

    return duplicate_counter, crawled_counter



if __name__ == '__main__':

    crawled_movies = movie_crawler(1, 3)
    crawled_series = series_crawler(1, 3)

    movies = remove_duplicate(crawled_movies)
    series = remove_duplicate(crawled_series)

    insert_movies = ready_for_insert(movies)
    insert_series = ready_for_insert(series)

    with open('crawl.log', 'a') as f:
        f.write(f'Crawled Successfully on {datetime.datetime.now()}\n{insert_movies[1] + insert_series[1]} New Movies and Series\n{insert_movies[0]} duplicate movies found.\n{insert_series[0]} duplicate series found.\n\n')