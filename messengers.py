import asyncio
from bot_instance import bot
from dal import get_all_users_telegram_ids, remove_user_from_db


async def send_message_to_all_users(message):
    user_info = get_all_users_telegram_ids()
    for element in user_info:
        try:
            telegram_id = element[0]
            user_database_id = element[1]
            await bot.bot.send_message(chat_id=telegram_id, text=message)
            print(f'Message sent to {telegram_id}')
        except Exception as e:
            remove_user_from_db(telegram_id=telegram_id, user_database_id=user_database_id)
            print(f'Failed to send message to {telegram_id}: {e}\n So The User and all related Records are Deleted!')

if __name__ == '__main__':
    message = """🎉 خبر خوب برای دوستداران فیلم و سریال 🎬

✨ زیرنویس فارسی به ربات ما اضافه شد! از این به بعد می‌تونید فیلم‌ها و سریال‌های مورد علاقتون رو با زیرنویس فارسی دانلود و تماشا کنید.

📥 برای دریافت زیرنویس‌ها، کافیه اسم فیلم یا سریال رو جستجو کنید و لینک زیرنویس رو همراه با لینک‌های دانلود ببینید!

از تماشای فیلم‌ها با زیرنویس لذت ببرید! 🎥🍿"""
    
    # Run the async function
    asyncio.run(send_message_to_all_users(message))
