import os
import pytest
import mysql.connector
from dal import is_duplicate, create_record_for_movies, movie_data_normalizer, find_movie_quality, find_series_season, get_movies_from_db
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


@pytest.fixture
def sample_links():
    data = [
        'https://5f8u2z8mn5qjqvfdxs59z5g6aw8djtnew25.kinguploadf2m15.xyz/Film/2023/The.Roundup.No.Way.Out.2023.1080p.WEB-DL.Farsi.Dubbed.New.Film2Media.mkv',
        'https://5f8u2z8mn5qjqvfdxs59z5g6aw8djtnew25.kinguploadf2m15.xyz/Film/2023/The.Roundup.No.Way.Out.2023.720p.WEB-DL.Farsi.Dubbed.New.Film2Media.mkv',
        'https://5f8u2z8mn5qjqvfdxs59z5g6aw8djtnew25.kinguploadf2m15.xyz/Film/2023/The.Roundup.No.Way.Out.2023.480p.WEB-DL.Farsi.Dubbed.New.Film2Media.mkv',
        'https://www.f2m91.fun/15828/damsel-2024/',
        'https://www.f2m91.fun/category/film/top-movies/',
        'https://5f8u2z8mn5qjqvfdxs59z5g6aw8djtnew27.kinguploadf2m15.xyz/Serial/The%20Sopranos/S01/',
        'https://5f8u2z8mn5qjqvfdxs59z5g6aw8djtnew27.kinguploadf2m15.xyz/Serial/The%20Sopranos/S02/',
    ]
    return data


@pytest.fixture
def sample_founded_movie_quality():
    data = [
        '1080p',
        '720p',
        '480p',
    ]
    return data


@pytest.fixture
def sample_founded_series_season():
    data = [
        'S01',
        'S02',
        'S03',
    ]
    return data


@pytest.fixture
def sample_inserted_record():
    data = [(4838, 'the-zone-of-interest-2023', 'https://www.f2m90.fun/15726/the-zone-of-interest-2023', None)]
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


def test_find_movie_quality(sample_links, sample_founded_movie_quality):
    """
    Test if find_movie_quality function works properly.
    """

    assert find_movie_quality(sample_links[0]) == [sample_founded_movie_quality[0]]
    assert find_movie_quality(sample_links[4]) == []


def test_find_series_season(sample_links, sample_founded_series_season):
    """
    Test if find_series_season function works properly.
    """

    assert find_series_season(sample_links[5]) == [sample_founded_series_season[0]]
    assert find_series_season(sample_links[6]) == [sample_founded_series_season[1]]


def test_get_movies_from_db(sample_inserted_record):
    """
    Test if get_movies_from_db function works properly.
    """

    assert get_movies_from_db() == sample_inserted_record