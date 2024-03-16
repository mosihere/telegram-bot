import os
import pytest
import mysql.connector
from dal import is_duplicate, create_record_for_movies, create_record_for_movie_links, get_movie_data, movie_data_normalizer
from mysql.connector import errorcode



@pytest.fixture
def sample_tuple_movies_data():
    data = [('https://www.f2m90.fun/15726/the-zone-of-interest-2023', 'the-zone-of-interest-2023')]
    return data


@pytest.fixture
def sample_tuple_movie_data():
    data = ('https://www.f2m90.fun/15726/the-zone-of-interest-2023', 'the-zone-of-interest-2023')
    return data


@pytest.fixture
def sample_json_movie_data():
    data = [
        {
        'link': 'https://www.f2m90.fun/15726/the-zone-of-interest-2023',
        'quality': '1080p',
        'codec': 'x265',
        'movie': {
            'name': 'the-zone-of-interest-2023',
            'published_at': 2023
        }
    },
    {
        'link': 'https://www.f2m90.fun/13246/shallow-water-2019',
        'quality': '720p',
        'codec': 'x264',
        'movie': {
            'name': 'shallow-water-2019',
            'published_at': 2019
        }
    }
    ]
    return data


@pytest.fixture
def sample_normalized_movie_data():
    data = [
        {
        'link': f'https://www.f2m90.fun/15726/the-zone-of-interest-2023\n',
        'quality_and_codec': '1080p - x265',
        'name': 'the-zone-of-interest-2023',
        'published_at': 2023
        },
        {
        'link': f'https://www.f2m90.fun/13246/shallow-water-2019\n',
        'quality_and_codec': '720p - x264',
        'name': 'shallow-water-2019',
        'published_at': 2019
        }
    ]
    return data


def test_is_duplicate():
    """
    Test if is_duplicate function works properly.
    """

    assert is_duplicate('friends') == True
    assert is_duplicate('NotExists') == False


def test_create_record_for_movies(sample_tuple_movies_data):
    """
    Test if create_record_for_movies function works properly.
    """
    
    assert create_record_for_movies(sample_tuple_movies_data) == f"We faced an error: 1062 (23000): Duplicate entry '{sample_tuple_movies_data[0][1]}' for key 'movies_movie.movies_movie_name_71b2d8ff_uniq'"


def test_movie_data_normalizer(sample_json_movie_data, sample_normalized_movie_data):
    """
    Test if movie_data_normalizer function works properly.
    """

    assert movie_data_normalizer(sample_json_movie_data) == sample_normalized_movie_data