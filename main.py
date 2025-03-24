import logging
import openai
import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.executor import start_webhook
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

API_TOKEN = os.getenv("BOT_TOKEN")
USER_CHAT_ID = os.getenv("USER_CHAT_ID")


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()

# Главное меню
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("✅ Отчёт"), KeyboardButton("📹 Видео"))
menu.add(KeyboardButton("📊 Моя фаза"), KeyboardButton("📖 Все фазы"))
menu.add(KeyboardButton("❓ Поддержка"))


# Уведомления
async def send_reminder():
    message = (
        "💪 Босс, настало время прокачать спину!\n\n"
        "🕘 Сейчас утро — самое время включить тело:\n"
        "✅ Дыхание животом\n✅ Мобилизация позвоночника\n✅ Активация кора и таза\n✅ Растяжка\n\n"
        "📹 Видео: Утренняя рутина\nhttps://youtube.com/playlist?list=..."
    )
    await bot.send_message(chat_id=USER_CHAT_ID, text=message)


async def send_evening_reminder():
    message = (
        "🌙 Босс, вечер — пора восстановить ось тела\n\n"
        "✅ Осанка\n✅ Копчик-блок\n✅ Растяжка таза\n\n"
        "📹 Видео: Вечерняя рутина + Копчик\nhttps://youtube.com/playlist?list=..."
    )
    await bot.send_message(chat_id=USER_CHAT_ID, text=message)


# Старт
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(
        "Босс, добро пожаловать в режим восстановления 💪\n\n"
        "Я помогу тебе восстановить спину, напоминать про упражнения и собирать отчёты.\n\n"
        "Выбирай действие:",
        reply_markup=menu
    )


# Видео
@dp.message_handler(lambda msg: msg.text == "📹 Видео")
async def video_links(message: types.Message):
    await message.answer("📺 Видео по упражнениям:")
    await message.answer("🕘 Утренняя рутина: https://youtube.com/playlist?list=...")
    await message.answer("🌙 Вечерняя рутина + Копчик-блок: https://youtube.com/playlist?list=...")


# Отчёт
@dp.message_handler(lambda msg: msg.text == "✅ Отчёт")
async def ask_report(message: types.Message):
    await message.answer(
        "Как прошла тренировка сегодня?\n\nОтметь, что сделал:\n"
        "✅ Утро\n✅ Вечер\n✅ Копчик-блок\n\n"
        "Как самочувствие от 1 до 10 или словами? 💬")


# Фаза
@dp.message_handler(lambda msg: msg.text == "📊 Моя фаза")
async def my_phase(message: types.Message):
    await message.answer("Сейчас ты на Фазе 1: Восстановление. Делай ежедневные упражнения 💪")


# Все фазы
@dp.message_handler(lambda msg: msg.text == "📖 Все фазы")
async def all_phases(message: types.Message):
    await message.answer("🧩 Все фазы:")
    await message.answer(
        "🔹 Фаза 1: Мобилизация и дыхание\n"
        "- Дыхание\n- Кошка-корова\n- Наклоны таза лёжа\n- Подтягивание колена\n- Скрутки\n- Поза ребенка"
    )
    await message.answer(
        "🔹 Фаза 2: Стабилизация\n"
        "- Стена\n- Вакуум\n- Лодочка\n- Планка\n- Поза голубя"
    )
    await message.answer(
        "🔹 Фаза 3: Укрепление\n"
        "- Мостик\n- Боковая планка\n- Усложненная лодочка\n- Стоячие упражнения\n- Мобилизация таза в движении"
    )


# Поддержка
@dp.message_handler(lambda msg: msg.text == "❓ Поддержка")
async def support(message: types.Message):
    await message.answer("Напиши свой вопрос, и я передам его твоему AI-тренеру 🧠")


# Обработка любых сообщений и запрос к OpenAI
@dp.message_handler()
async def handle_any(message: types.Message):
    now = datetime.now().strftime('%d.%m %H:%M')
    user_input = message.text
    log_msg = f"[ОТЧЁТ] {now} — {message.from_user.full_name}: {user_input}"
    print(log_msg)

    await message.answer("Принял, босс ✅ Отправляю тренеру...")

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты AI-тренер по восстановлению позвоночника. Отвечай кратко, дружелюбно и точно."},
                {"role": "user", "content": user_input}
            ]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = f"Ошибка от тренера: {e}"

    await message.answer(f"🧠 Тренер ответил:\n{reply}")


if __name__ == '__main__':
    scheduler.add_job(send_reminder, 'cron', hour=8, minute=0)
    scheduler.add_job(send_evening_reminder, 'cron', hour=23, minute=0)
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
