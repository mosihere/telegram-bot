import os
from dal import movie_endpoint, movie_data_normalizer
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, InlineQueryHandler, CallbackQueryHandler

TOKEN = os.environ['BOT_TOKEN']
BOT_USERNAME = '@shodambot'



# Commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    # keyboard = [
    #     [
    #         InlineKeyboardButton("film", callback_data="1"),
    #         InlineKeyboardButton("idk", callback_data="2"),
    #     ],
    #     [InlineKeyboardButton("idk", callback_data="3")],
    # ]

    # reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text('🎥 چه فیلمی میخوای\n\n✅john wick\n\n🔍سرچش کن: ')




# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     await query.answer()
#     print(query.data)
#     await query.edit_message_text(text='Enter Movie/Series Name: ')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('من میتونم لینک دانلود مستقیم فیلم بهت بدم بدون سانسور :)\n\n✅ -> evil dead')


# Responses

def handle_response(text: str) -> str:

    movie = movie_endpoint(text)
    normalized_data = movie_data_normalizer(movie)
    movie_name = normalized_data[0].get('name')
    published_date = normalized_data[0].get('published_at')

    lst = []
    for movie in normalized_data:
        print(f'movie -> {movie}')
        lst.append(movie.get('quality_and_codec'))
        lst.append(movie.get('link'))

    if published_date:
        lst.insert(0, f'سال انتشار{published_date}\n\n')

    lst.insert(0, f'🍿{movie_name}\n\n')
    lst.insert(0, '🎞️ کیفیت های مختلف 🎞️\n\n')
    lst.insert(0, f'❗️برای دانلود VPN خود را خاموش کنید❗️\n\n')

    
    return f'\n----------------------------------\n'.join(lst)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    message_type = update.message.chat.type
    text = update.message.text.replace(' ', '-')
    print(text)

    print(f'User {update.message.chat.id} in {message_type}: "{text}"')


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
    # app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler('help', help_command))


    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Polls the bot
    print('Bot is up and running...')
    app.run_polling(timeout=5)
