import asyncio
import logging
import os
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("8580836716:AAHPPbmugu2cAcWJ0mH3NQ2TQ0o92nZVrzE")  # Токен из BotFather
ADMIN_ID = os.getenv("8884529763")    # Твой Telegram ID

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# --- База данных ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        referrer_id INTEGER,
        ref_count INTEGER DEFAULT 0,
        requests_left INTEGER DEFAULT 3
    )""")
    conn.commit()
    conn.close()

# --- Реферальная система ---
def add_user(user_id, username, referrer_id=None):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, referrer_id) VALUES (?, ?, ?)",
              (user_id, username, referrer_id))
    if referrer_id:
        c.execute("UPDATE users SET ref_count = ref_count + 1, requests_left = requests_left + 1 WHERE user_id = ?",
                  (referrer_id,))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

# --- Хендлеры ---
@dp.message(CommandStart())
async def start(message: Message):
    args = message.text.split()
    referrer_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
    add_user(message.from_user.id, message.from_user.username, referrer_id)
    
    # Реферальная ссылка
    bot_username = (await bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={message.from_user.id}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Пробив", callback_data="search")],
        [InlineKeyboardButton(text="👤 Мой профиль", callback_data="profile")],
        [InlineKeyboardButton(text="🎁 Пригласить друга", url=f"https://t.me/share/url?url={ref_link}")]
    ])
    
    user = get_user(message.from_user.id)
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n"
        f"У тебя {user[4] if user else 3} запросов.\n"
        f"Приглашай друзей — получай +1 запрос за каждого.",
        reply_markup=keyboard
    )

@dp.message(Command("admin"))
async def admin(message: Message):
    if str(message.from_user.id) != ADMIN_ID:
        await message.answer("Нет доступа.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выдать себе 100 запросов", callback_data="give_100")],
        [InlineKeyboardButton(text="Статистика", callback_data="stats")]
    ])
    await message.answer("Админ-панель:", reply_markup=keyboard)

# --- Запуск ---
async def main():
    init_db()
    await dp.start_polling(bot, handle_signals=False)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
