import os
import logging
from uuid import uuid4
from dal import movie_data_normalizer, movie_links_endpoint, movie_endpoint
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, InlineQueryHandler, ChosenInlineResultHandler

TOKEN = os.environ['BOT_TOKEN']
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


async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    if not query:
        return
    inline_options = []
    for movie in search_movie(update.inline_query.query.replace(' ', '-')):
        movie_id = movie.get('id')
        inline_options.append(
        InlineQueryResultArticle(
                id=movie_id,
                title=movie.get('name'),
                input_message_content=InputTextMessageContent(handle_response(movie_id))
        )
        )
    await context.bot.answer_inline_query(update.inline_query.id, inline_options)


def search_movie(title: str):
    movie = movie_endpoint(title)
    return movie

# Responses

def handle_response(movie_id: str) -> str:

    movie = movie_links_endpoint(movie_id)
    normalized_data = movie_data_normalizer(movie)
    if not normalized_data:
        return 'هنوز این فیلم رو نداریم :('
    movie_name = normalized_data[0].get('name')
    published_date = normalized_data[0].get('published_at')

    lst = []
    for movie in normalized_data:
        lst.append('✔️' + movie.get('quality_and_codec'))
        lst.append(movie.get('link'))

    if published_date:
        lst.insert(0, f'🍿{movie_name}\n\n📆 {published_date}\n\n')
        lst.insert(0, '🎞️ کیفیت های مختلف 🎞️\n\n')
        lst.insert(0, f'❗️برای دانلود VPN خود را خاموش کنید❗️\n\n')

    else:
        lst.insert(0, f'🍿{movie_name}\n\n')
        lst.insert(0, '🎞️ کیفیت های مختلف 🎞️\n\n')
        lst.insert(0, f'❗️برای دانلود VPN خود را خاموش کنید❗️\n\n')

    
    return f'\n----------------------------------\n'.join(lst)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    message_type = update.message.chat.type
    text = update.message.text.replace(' ', '-')

    with open('users.log', 'a') as f:
        f.write(f'User {update.message.chat.id} in {message_type}: "{text}"\n')


    if message_type == 'group':

        if BOT_USERNAME in text:
            print(text)
            new_text = text.replace(BOT_USERNAME, '').strip().lstrip('-')
            print(new_text)
            response = handle_response(new_text)

        else:
            return
        
    else:
        response = handle_response(text)


    print(f'Bot: {response}')

    if len(response) > 4096:
        for x in range(0, len(response), 4096):
            await update.message.reply_text(response[x: x+4096])

    else:
        await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f'Update {update} caused error {context.error}')



if __name__ == '__main__':

    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start))

    # Messages
    # app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # on inline queries - show corresponding inline results
    app.add_handler(InlineQueryHandler(inline_query))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Bot is up and running...')
    app.run_polling(timeout=20)
