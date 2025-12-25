
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

API_TOKEN = "8586175130:AAG_rDh-eFygUTayGukpBOWhWQrijdLS-rA"
ADMIN_ID = 701821593

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

USERS_FILE = "users.json"


def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data)
        except Exception:
            return set()
    return set()


def save_users(users_set):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(users_set), f)


users = load_users()


# ============================
# /start
# ============================
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    if message.chat.type != "private":
        await message.answer(
            "Чтобы подписаться на рассылку, зайдите ко мне в ЛС и нажмите /start 👍"
        )
        return

    users.add(message.chat.id)
    save_users(users)
    await message.answer(
        "Спасибо! Вы подписаны на рассылку 🔔\n\n"
        "Теперь вы будете получать рекламные посты и акции."
    )


# ============================
# /stop
# ============================
@dp.message_handler(commands=["stop"])
async def stop_handler(message: types.Message):
    if message.chat.id in users:
        users.remove(message.chat.id)
        save_users(users)
        await message.answer("Вы успешно отписались от рассылки ❌")
    else:
        await message.answer("Вы не были подписаны 🙂")


# ============================
# /send (рассылка)
# ============================
@dp.message_handler(commands=["send"])
async def send_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not users:
        await message.answer("Нет подписчиков для рассылки.")
        return

    if not message.reply_to_message:
        await message.answer("Сделай ответ /send на сообщение, которое нужно разослать.")
        return

    post = message.reply_to_message
    sent = 0

    for uid in list(users):
        try:
            await bot.copy_message(
                chat_id=uid,
                from_chat_id=post.chat.id,
                message_id=post.message_id,
            )
            sent += 1
        except Exception:
            pass

    await message.answer(f"Разослано {sent} пользователям ✅")


# ============================
# /stats
# ============================
@dp.message_handler(commands=["stats"])
async def stats_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"В рассылке сейчас: {len(users)} пользователей.")


# ============================
# Приветствие новых участников группы
# ============================
@dp.message_handler(content_types=['new_chat_members'])
async def welcome_new_user(message: types.Message):
    bot_info = await bot.get_me()

    for user in message.new_chat_members:
        if user.id == bot_info.id:
            continue

        username = f"@{user.username}" if user.username else user.full_name

        await message.answer(
            f"{username} 🔥 Добро пожаловать!\n\n"
            f"Чтобы получать акции и новости Motoland — подпишись на нашего бота:\n"
            f"👉 https://t.me/Motoland_Notify_bot?start=1\n\n"
            f"Нажмите «Start» 👍"
        )


# ============================
# Запуск
# ============================
if __name__ == "__main__":
    print("Bot is running...")
    executor.start_polling(dp, skip_updates=True)
