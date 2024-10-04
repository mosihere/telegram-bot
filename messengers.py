import asyncio
from bot_instance import bot
from utils import get_datetime_info
from dal import get_all_users_telegram_ids, remove_user_from_db



async def send_message_to_all_users(message: str, reply_markup=None, parse_mode=None) -> None:
    """
    Sending Message To Bot Users

    Args:
        message: str
        reply_markup
        parse_mode
    
    Returns:
        None
    """

    user_info = get_all_users_telegram_ids()

    datetime_info = get_datetime_info()
    year = datetime_info.get('year')
    month = datetime_info.get('month')
    day = datetime_info.get('day')
    hour = datetime_info.get('hour')
    minute = datetime_info.get('minute')
    second = datetime_info.get('second')
    print(f'Sending Message To Users On {year}-{month}-{day}\nTime: {hour}:{minute}:{second}')

    for element in user_info:
        try:
            telegram_id = element[0]
            user_database_id = element[1]
            await bot.bot.send_message(chat_id=telegram_id, text=message, reply_markup=reply_markup, parse_mode=parse_mode)
            print(f'Message sent to {telegram_id}')
        except Exception as e:
            remove_user_from_db(telegram_id=telegram_id, user_database_id=user_database_id)
            print(f'Failed to send message to {telegram_id}: {e}\n So The User and all related Records are Deleted!')
    print()

if __name__ == '__main__':
    message = """

"""
    # Run the async function
    asyncio.run(send_message_to_all_users(message, parse_mode='HTML'))
