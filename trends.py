import random
import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from messengers import send_message_to_all_users
from utils import TMDB_BEARER_TOKEN, clean_movie_name_for_api, get_datetime_info
from dal import get_trending_movies, mark_trending_movie, suggest_trending_movies, clear_trending_movie



async def send_trending_movies():
    """Send a message with trending movies and buttons for download links."""
    # Fetch trending movies from your database
    trending_movies = suggest_trending_movies()

    # Sample 5 movies if there are enough
    random_trend_movies = random.sample(trending_movies, min(len(trending_movies), 5))

    # Prepare the message to send
    message = "<b>🔥 فیلم های پیشنهادی این هفته 🔥</b>"
    
    # Create a list to hold the buttons
    keyboard = []

    for movie in random_trend_movies:
        movie_id = movie[0]  # Assuming you have the movie ID
        movie_name = movie[1]
        
        # Add a button for download links for each movie
        keyboard.append([
            InlineKeyboardButton(text=movie_name, callback_data=f"trending_links:{movie_id}")
        ])

    # Create the InlineKeyboardMarkup with the buttons
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send the message to all users
    await send_message_to_all_users(message, reply_markup, parse_mode='HTML')

def main():
    # Clear previous trending movies
    clear_trending_movie()
    
    # Fetch new trending movies
    trend_movies = get_trending_movies(TMDB_BEARER_TOKEN)
    for element in trend_movies:
        movie_title = element['title']
        cleaned_movie_name = clean_movie_name_for_api(movie_title)
        mark_trending_movie(cleaned_movie_name)

    # Send trending movies to users
    asyncio.run(send_trending_movies())

if __name__ == '__main__':
    main()
