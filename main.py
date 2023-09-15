import os
from dal import read_record, get_links
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

    await update.message.reply_text('🎥 Search For Movie\n\n✅john wick\n\n🔍What Movie You Want: ')




# async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Parses the CallbackQuery and updates the message text."""
#     query = update.callback_query

#     # CallbackQueries need to be answered, even if no notification to the user is needed
#     # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
#     await query.answer()
#     print(query.data)
#     await query.edit_message_text(text='Enter Movie/Series Name: ')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('You can Ask me for finding Movies :)\n\n✅ -> evil dead')


# Responses

def handle_response(text: str) -> str:

    links_and_quality = list()

    records = read_record(text)

    try:
        links, movie_name, quality = get_links(records)

        data = list(zip(links, quality))
        
        for link, quality in data:
            links_and_quality.append(quality)
            links_and_quality.append(link)

        links_and_quality.insert(0, f'🍿{movie_name.title()}\n\n')
        links_and_quality.insert(0, '🎞️ Differenet Qualites 🎞️\n\n' )
        download_links = f'\n----------------------------------\n'.join(links_and_quality)

        return download_links
    
    except TypeError:
        return '😔 We Do not have that Movie yet!'



async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    message_type = update.message.chat.type
    text = update.message.text.replace(' ', '-')

    print(f'User {update.message.chat.id} in {message_type}: "{text}"')


    if message_type == 'group':

        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
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
    app.run_polling()