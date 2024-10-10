import random
import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from constants import TMDB_BEARER_TOKEN
from utils import clean_movie_name_for_api
from messengers import send_message_to_all_users
from dal import suggest_trending_movies, clear_trending_movie, mark_trending_movie, get_trending_movies


async def send_trending_movies() -> None:
    """Send a message with trending movies and buttons for download links."""
    trending_movies = suggest_trending_movies()
    random_trend_movies = random.sample(trending_movies, min(len(trending_movies), 5))

    message = "<b>🔥 فیلم های پیشنهادی این هفته 🔥</b>"
    keyboard = []

    for movie in random_trend_movies:
        movie_id = movie[0]
        movie_name = movie[1]
        button = InlineKeyboardButton(text=movie_name, callback_data=f"trending_links:{movie_id}")
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_to_all_users(message, reply_markup, parse_mode='HTML')


async def send_suggested_movie(movie_id: int, movie_name: str) -> None:
    """Send a message with a specific movie and button for download links."""
    message = "<b>🔥 فیلم پیشنهادی ما 🔥</b>"
    keyboard = [[InlineKeyboardButton(text=movie_name, callback_data=f"trending_links:{movie_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message_to_all_users(message, reply_markup, parse_mode='HTML')


def send_automatic_trending():
    """Automatic: Clear previous movies, fetch new ones, and send trending movies."""
    clear_trending_movie()
    trend_movies = get_trending_movies(authorization=TMDB_BEARER_TOKEN)
    for element in trend_movies:
        movie_name = element['title']
        cleaned_movie_name = clean_movie_name_for_api(movie_name)
        mark_trending_movie(cleaned_movie_name)

    asyncio.run(send_trending_movies())


def send_manual_movie(movie_id: int, movie_name: str):
    """Manual: Send a single specific movie."""
    asyncio.run(send_suggested_movie(movie_id, movie_name))


if __name__ == '__main__':
    import sys

    if len(sys.argv) == 1:
        # Default to automatic mode
        send_automatic_trending()
    elif len(sys.argv) == 3:
        # Manual mode with provided movie details
        movie_id = int(sys.argv[1])
        movie_name = sys.argv[2]
        send_manual_movie(movie_id, movie_name)
    else:
        print("Usage: python trends.py [movie_id movie_name]")
