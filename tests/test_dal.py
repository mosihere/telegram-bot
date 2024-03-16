import os
import pytest
import mysql.connector
from dal import is_duplicate, create_record_for_movies
from mysql.connector import errorcode



@pytest.fixture
def sample_movie_data():
    data = [('https://www.f2m90.fun/15726/the-zone-of-interest-2023', 'the-zone-of-interest-2023')]
    return data


def test_is_duplicate():
    """
    Test if is_duplicate function works properly.
    """

    assert is_duplicate('friends') == True
    assert is_duplicate('NotExists') == False


def test_create_record_for_movies(sample_movie_data):
    """
    Test if create_record_for_movies function works properly.
    """
    
    assert create_record_for_movies(sample_movie_data) == f"We faced an error: 1062 (23000): Duplicate entry '{sample_movie_data[0][1]}' for key 'movies_movie.movies_movie_name_71b2d8ff_uniq'"