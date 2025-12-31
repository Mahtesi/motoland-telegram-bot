import os
import json
import asyncio
from typing import Set

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command

USERS_FILE = "users.json"


def load_users() -> Set[int]:
    if not os.path.exists(USERS_FILE):
        return set()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(int(x) for x in data)
    except Exception:
        return set()


def save_users(users: Set[int]) -> None:
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(users)), f, ensure_ascii=False, indent=2)


async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = int(os.getenv("ADMIN_ID", "0"))

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not admin_id:
        raise RuntimeError("ADMIN_ID is not set")

    bot = Bot(token=token)
    dp = Dispatcher()

    users = load_users()

    # /start — подписка (только в личке)
    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        if message.chat.type != "private":
            await message.answer(
                "Чтобы подписаться на рассылку — откройте бота в личке и нажмите /start 👍\n"
                "👉 https://t.me/Motoland_Notify_bot?start=1"
            )
            return

        users.add(message.chat.id)
        save_users(users)

        await message.answer(
            "Спасибо! Вы подписаны на рассылку 🏍️🔔\n\n"
            "Теперь вы будете получать акции и новости Motoland."
        )

    # /stop — отписка
    @dp.message(Command("stop"))
    async def cmd_stop(message: types.Message):
        if message.chat.type != "private":
            await message.answer("Команда работает только в личных сообщениях с ботом.")
            return

        if message.chat.id in users:
            users.remove(message.chat.id)
            save_users(users)
            await message.answer("Вы успешно отписались ❌")
        else:
            await message.answer("Вы не были подписаны 🙂")

    # /stats — статистика (только админ)
    @dp.message(Command("stats"))
    async def cmd_stats(message: types.Message):
        if message.from_user.id != admin_id:
            return
        await message.answer(f"В рассылке сейчас: {len(users)} пользователей.")

    # /send — рассылка (только админ) + обязательно reply на пост
    @dp.message(Command("send"))
    async def cmd_send(message: types.Message):
        if message.from_user.id != admin_id:
            return

        if not message.reply_to_message:
            await message.answer("Сделай Reply на пост и в ответ напиши /send")
            return

        if not users:
            await message.answer("Нет подписчиков для рассылки.")
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
                # пользователь мог заблокировать бота / удалить чат и т.д.
                pass

        await message.answer(f"Разослано {sent} пользователям ✅")

    # Приветствие нового пользователя в ГРУППЕ (не в канале)
    # ВАЖНО: это работает только если бот добавлен в группу и видит события (обычно хватает обычных прав).
    @dp.message(F.new_chat_members)
    async def welcome_new_user(message: types.Message):
        me = await bot.get_me()
        for user in message.new_chat_members:
            if user.id == me.id:
                continue

            username = f"@{user.username}" if user.username else user.full_name
            await message.answer(
                f"{username} 🔥 Добро пожаловать!\n\n"
                f"Чтобы получать акции и новости Motoland — подпишись на бота:\n"
                f"👉 https://t.me/Motoland_Notify_bot?start=1\n\n"
                f"Нажмите «Start» 👍"
            )

    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
