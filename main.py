import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Получаем токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("Токен не найден! Добавьте BOT_TOKEN в Variables")

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот и я работаю!")

# Обработчик всех остальных сообщений (опционально)
@dp.message()
async def echo_message(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")

# Функция запуска бота
async def main():
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
