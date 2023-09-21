import re
import time
import requests
from dal import create_record, is_duplicate


# Careful! Just run this module when you want crawl movies.


BASE_URL = "https://www.f2m12.top"



def movie_crawler(start_page: int, end_page: int) -> list:
    data = list()

    for page in range(start_page, end_page + 1):

        response = requests.get(f'{BASE_URL}/page/{page}')

        time.sleep(2)

        links = re.findall(f'{BASE_URL}/\d*/\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*', response.text)
        data.append(list(set(links)))
        
    return data


def series_crawler(start_page: int, end_page: int) -> list:
    data = list()

    for page in range(start_page, end_page + 1):

        response = requests.get(f'{BASE_URL}/category/دانلود-سریال/page/{page}')

        time.sleep(2)

        links = re.findall(f'{BASE_URL}/\d*/\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*\w*[-]*\d*', response.text)
        data.append(list(set(links)))
        
    return data



def remove_duplicate(movie_list: list) -> list:
    new_list = list()

    for part in movie_list:
        for movie in part:
            new_list.append(movie)

    normalized_data = list(set(new_list))

    return normalized_data


def ready_for_insert(movies: list) -> None:
    movies_data = list()
    movies_with_published_date = list()

    for data in movies:

        url = data
        movie_name = data.split('/')
        movie_name = movie_name[-1]

        if is_duplicate(movie_name):
            continue

        
        published_date:str = movie_name.split('-')
        published_date = published_date[-1]

        if published_date.isnumeric() and len(published_date) == 4:
            info = (url, movie_name, published_date)
            movies_with_published_date.append(info)

        else:
            data = (url, movie_name)
            movies_data.append(data)

    create_record(movies_data)
    create_record(movies_with_published_date, has_published_date=True)




if __name__ == '__main__':

    crawled_movies = movie_crawler(1, 10)
    crawled_series = series_crawler(1, 10)

    movies = remove_duplicate(crawled_movies)
    series = remove_duplicate(crawled_series)

    ready_for_insert(movies)
    ready_for_insert(series)
