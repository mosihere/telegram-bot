import re
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters, InlineQueryHandler, CallbackQueryHandler
from bot_instance import bot
from constants import API_KEY
from utils import get_datetime_info, clean_movie_name_for_api, movie_data_normalizer, normalized_imdb_info
from dal import (
    movie_links_endpoint,
    movie_endpoint,
    get_movie_imdb_info,
    create_user_record,
    create_user_search_record,
    get_user_from_db_by_telegram_id,
    update_user_last_use
)



# Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    telegram_id = user.id
    datetime_info = get_datetime_info(compatible_with_db=True)
    username = user.username

    if user_id:= get_user_from_db_by_telegram_id(telegram_id):
        await update_user_last_use(datetime_info, user_id)
    
    else:
        first_name = user.first_name
        last_name = user.last_name

        user_data = {
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }
        await create_user_record(user_data)

    if username:
        await update.message.reply_text(
            f"""
                سلام  {username} عزیز 🎬

👋 خوش اومدی به ربات دانلود فیلم و سریال 🎥

✨ فقط کافیه اسم فیلم یا سریال مورد نظرت رو اینگیلیسی تایپ کنی تا نتایج رو ببینی

@shodambot enemy

📲 حتی میتوتی به همین روش، توی گروه‌ها و چت خصوصی هم از ربات استفاده کنی! 
            """
)
    else:
        await update.message.reply_text(
            """
                سلام دوست من 🎬
👋 خوش اومدی به ربات دانلود فیلم و سریال 🎥

✨ فقط کافیه اسم فیلم یا سریال مورد نظرت رو اینگیلیسی تایپ کنی تا نتایج رو ببینی

@shodambot enemy

📲 حتی میتوتی به همین روش، توی گروه‌ها و چت خصوصی هم از ربات استفاده کنی! 
            """
)


async def movie_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('🎥اسم فیلم یا سریال مورد نظرت رو بنویس\nاطالاعاتش رو برات میارم مثل سال ساخت، بازیگراش، کارگردانش، نمرات imdb و ...')


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.inline_query.query
    telegram_id = update.inline_query.from_user.id

    if len(query) < 3:
        return

    inline_options = []
    movie_results = await search_movie(query.replace(' ', '-'), telegram_id)

    # Check if the result indicates a rate limit was exceeded
    if movie_results and movie_results[0].get('id') == "rate_limit":
        inline_options.append(
            InlineQueryResultArticle(
                id="rate_limit_notice",
                title="Rate limit exceeded",
                input_message_content=InputTextMessageContent("You've reached the rate limit. Please try again later."),
                description="Too many requests. Please wait a few moments.",
            )
        )
    else:
        for movie in movie_results:
            movie_id = movie.get('id')
            movie_name = movie.get('name')
            poster_url = movie.get('poster_url')
            inline_options.append(
                InlineQueryResultArticle(
                    id=str(movie_id),
                    title=movie_name,
                    thumbnail_url=poster_url,
                    input_message_content=InputTextMessageContent(movie_name),
                    description=movie.get('description', ''),
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("لینک های دانلود", callback_data=f"links:{movie_id}")],
                        [InlineKeyboardButton("اطلاعات فیلم", callback_data=f"info:{movie_name}")]
                    ])
                )
            )
    
    await update.inline_query.answer(inline_options)

    # Get User Info
    inline_query = update.inline_query
    user_object = inline_query.from_user
    telegram_user_id = user_object.id
    database_user_id = get_user_from_db_by_telegram_id(telegram_user_id)
    
    # Get DateTime Info
    datetime_info = get_datetime_info(compatible_with_db=True)

    if database_user_id:
        await update_user_last_use(datetime_info, database_user_id)

    else:
        username = user_object.username
        first_name = user_object.first_name
        last_name = user_object.last_name
        user_data = {
            'telegram_id': telegram_user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
            }
        result = await create_user_record(user_data)
        database_user_id = result.get('id')

    user_search_data = {
        'user': database_user_id,
        'query': query,
    }
    await create_user_search_record(user_search_data)

    await update.inline_query.answer(inline_options)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    user_object = query.from_user
    telegram_user_id = user_object.id
    database_user_id = get_user_from_db_by_telegram_id(telegram_user_id)

    # Get DateTime Info
    datetime_info = get_datetime_info(compatible_with_db=True)

    if database_user_id:
        await update_user_last_use(datetime_info, database_user_id)

    else:
        username = user_object.username
        first_name = user_object.first_name
        last_name = user_object.last_name
        user_data = {
            'telegram_id': telegram_user_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
            }
        database_user_id = await create_user_record(user_data)

    if data.startswith("trending_links:"):
        movie_id = data.split(":")[1]
        response = await handle_response(movie_id, telegram_user_id)
        await context.bot.send_message(chat_id=telegram_user_id, text=response, parse_mode='HTML')

    elif data.startswith("links:"):
        movie_id = data.split(":")[1]
        response = await handle_response(movie_id, telegram_user_id)
        await context.bot.send_message(chat_id=query.from_user.id, text=response, parse_mode='HTML')

    elif data.startswith("info:"):
        final_result = list()
        movie_name = data.split(":")[1]
        cleaned_movie_name = clean_movie_name_for_api(movie_name)
        movie_info = await get_movie_imdb_info(cleaned_movie_name, API_KEY)
        result = normalized_imdb_info(movie_info)
        
        for key, value in result.items():
            final_result.append(f'{key}: {value}')
        
        await context.bot.send_message(chat_id=query.from_user.id, text='\n\n'.join(final_result))


async def search_movie(title: str, telegram_id: int):
    movie = await movie_endpoint(title, telegram_id)
    return movie


# Responses
async def handle_response(movie_id: str, telegram_id: int) -> str:
    movie = await movie_links_endpoint(movie_id, telegram_id)

    if isinstance(movie, dict):
        return movie.get('detail')
    
    normalized_data = movie_data_normalizer(movie)
    if not normalized_data:
        return 'هنوز این فیلم رو نداریم :('
    movie_name = normalized_data[0].get('name')
    published_date = normalized_data[0].get('published_at')
    subtitle_url = normalized_data[0].get('subtitle_url')
    season_episode_pattern = re.compile(r'[sS]\d{2}[eE]\d{2}')
    collection_pattern = re.compile(r'([^/]+?\.\d{4})|([^/]+\.\d{4}\.\d{4})')

    movie_data_list = []
    for movie in normalized_data:
        movie_data_list.append(f"<b>✔️ {movie.get('quality_and_codec')}</b>")
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
        movie_data_list.insert(0, f'🔗 <a href="{subtitle_url}">Subtitle</a>\n')
        movie_data_list.insert(0, f'<b>🍿{movie_name}</b>\n<b>📆 {published_date}</b>\n')
        movie_data_list.insert(0, f'❗️برای دانلود VPN خود را خاموش کنید❗️\n')

    else:
        movie_data_list.insert(0, f'🔗 <a href="{subtitle_url}">Subtitle</a>\n')
        movie_data_list.insert(0, f'<b>🍿{movie_name}</b>\n')
        movie_data_list.insert(0, f'❗️برای دانلود VPN خود را خاموش کنید❗️\n')

    return f'\n----------------------------------\n'.join(movie_data_list)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update {update} caused error {context.error}')



if __name__ == '__main__':

    # Commands
    bot.add_handler(CommandHandler('start', start))
    bot.add_handler(CommandHandler('getinfo', movie_info))

    # Messages
    # app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # on inline queries - show corresponding inline results
    bot.add_handler(InlineQueryHandler(inline_query))
    bot.add_handler(CallbackQueryHandler(button))

    # Errors
    bot.add_error_handler(error)

    # Polls the bot
    print('Bot is up and running...')
    bot.run_polling(timeout=20)
