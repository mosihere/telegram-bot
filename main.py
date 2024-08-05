import re
import os
import logging
from datetime import datetime
from dal import movie_data_normalizer, movie_links_endpoint, movie_endpoint, get_movie_imdb_info, normalized_imdb_info, user_data_log
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, InlineQueryHandler, CallbackQueryHandler

TOKEN = os.environ.get('BOT_TOKEN')
API_KEY = os.environ.get('API_KEY')
BOT_USERNAME = '@shodambot'


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('🎥 چه فیلمی میخوای\n\n🔍آیدی بات رو منشن کن و جلوش سرچ کن تا نتایج جست و جو رو ببینی\n\n💪حتی تو گروه و پی وی دیگران هم میتونی اینکار رو انجام بدی :)\n\nاینشکلی:\n\n@shodambot friends✅')


async def movie_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('🎥اسم فیلم یا سریال مورد نظرت رو بنویس\nاطالاعاتش رو برات میارم مثل سال ساخت، بازیگراش، کارگردانش، نمرات imdb و ...')


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    if len(query) < 3:
        return
    inline_options = []
    for movie in await search_movie(query.replace(' ', '-')):
        movie_id = movie.get('id')
        movie_name = movie.get('name')
        inline_options.append(
            InlineQueryResultArticle(
                id=str(movie_id),
                title=movie.get('name'),
                input_message_content=InputTextMessageContent(movie['name']),
                description=movie.get('description', ''),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("لینک های دانلود", callback_data=f"links:{movie_id}")],
                    [InlineKeyboardButton("اطلاعات فیلم", callback_data=f"info:{movie_name}")]
                ])
            )
        )
    
    # Get User Info
    inline_query = update.inline_query
    user = inline_query.from_user
    
    # Get DateTime Info
    datetime_info = datetime.now()
    year = datetime_info.year
    month = datetime_info.month
    day = datetime_info.day
    hour = datetime_info.hour + 4
    minute = datetime_info.minute + 30
    second = datetime_info.second

    user_data = (
        f"Query ID: {inline_query.id}\n"
        f"From: {user.first_name} {user.last_name} (@{user.username})\n"
        f"User ID: {user.id}\n"
        f"Query: {query}\n"
        f"Date: {year:04d}-{month:02d}-{day:02d}\n"
        f"Time: {hour:02d}:{minute:02d}:{second:02d}\n"
    )
    user_data_log(user_data)

    await update.inline_query.answer(inline_options)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data

    if data.startswith("links:"):
        movie_id = data.split(":")[1]
        response = handle_response(movie_id)
        await query.edit_message_text(text=response, parse_mode='Html')

    elif data.startswith("info:"):
        final_result = list()
        movie_name = data.split(":")[1]
        movie_info = get_movie_imdb_info(movie_name, API_KEY)
        result = normalized_imdb_info(movie_info)
        
        for key, value in result.items():
            final_result.append(f'{key}: {value}')
        
        await query.edit_message_text('\n\n'.join(final_result))


async def search_movie(title: str):
    movie = await movie_endpoint(title)
    return movie

# Responses
def handle_response(movie_id: str) -> str:

    movie = movie_links_endpoint(movie_id)
    normalized_data = movie_data_normalizer(movie)
    if not normalized_data:
        return 'هنوز این فیلم رو نداریم :('
    movie_name = normalized_data[0].get('name')
    published_date = normalized_data[0].get('published_at')

    season_episode_pattern = re.compile(r'[sS]\d{2}[eE]\d{2}')
    collection_pattern = re.compile(r'([^/]+?\.\d{4})|([^/]+\.\d{4}\.\d{4})')

    movie_data_list = []
    for movie in normalized_data:
        movie_data_list.append('✔️' + movie.get('quality_and_codec'))
        raw_link = movie.get('link')
        is_collection = re.search('[cC]ollection', raw_link)
        get_season_episode = season_episode_pattern.search(raw_link)

        if get_season_episode:
            html_link = f'📥 {get_season_episode.group(0).upper()} <a href="{raw_link}">Download</a>\n'
            movie_data_list.append(html_link)
            continue

        elif is_collection:
            match = collection_pattern.search(raw_link)
            if match:
                name_normalizer = lambda string: string.replace('.', ' ')
                info = match.group(0)
                html_link = f'📥 {name_normalizer(info)} <a href="{raw_link}">Download</a>\n'
                movie_data_list.append(html_link)
                continue
            pass

        else:
            html_link = f'📥 <a href="{raw_link}">Download</a>\n'
            movie_data_list.append(html_link)

    if published_date:
        movie_data_list.insert(0, f'🍿{movie_name}\n\n📆 {published_date}\n\n')
        movie_data_list.insert(0, '🎞️ کیفیت های مختلف 🎞️\n\n')
        movie_data_list.insert(0, f'❗️برای دانلود VPN خود را خاموش کنید❗️\n\n')

    else:
        movie_data_list.insert(0, f'🍿{movie_name}\n\n')
        movie_data_list.insert(0, '🎞️ کیفیت های مختلف 🎞️\n\n')
        movie_data_list.insert(0, f'❗️برای دانلود VPN خود را خاموش کنید❗️\n\n')

    return f'\n----------------------------------\n'.join(movie_data_list)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update {update} caused error {context.error}')



if __name__ == '__main__':

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('getinfo', movie_info))

    # Messages
    # app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # on inline queries - show corresponding inline results
    app.add_handler(InlineQueryHandler(inline_query))
    app.add_handler(CallbackQueryHandler(button))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Bot is up and running...')
    app.run_polling(timeout=20)
