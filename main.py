import asyncio
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import BOT_TOKEN, CHANNEL_ID, JACKPOT_CHANCE
from database import Database

# Подключаемся к базе данных
db = Database()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Смайлики для красоты
EMOJI = {
    "slot": "🎰",
    "dice": "🎲",
    "success": "✅",
    "fail": "❌",
    "fire": "🔥",
    "gift": "🎁",
    "rocket": "🚀",
    "gem": "💎"
}

# Проверка выигрыша (777)
def check_jackpot():
    return random.randint(1, 100) <= JACKPOT_CHANCE

# Команда /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    if message.chat.id != CHANNEL_ID:
        return
    
    user = message.from_user
    db.create_user(user.id, user.username, user.first_name)
    
    text = f"""{EMOJI['slot']} *ВЕЧНАЯ ЛУДКА* {EMOJI['slot']}

*Как играть:*
1. Отправь {EMOJI['slot']} или {EMOJI['dice']} в комментарии
2. Если выпадет 7️⃣7️⃣7️⃣ — лови второй шанс
3. За 30 секунд нужно поймать ещё 7️⃣7️⃣7️⃣
4. Потом финал и супер-приз!

*Команды:*
/rules — правила
/top — топ игроков"""
    
    await message.reply(text)

# Команда /rules
@dp.message_handler(commands=['rules'])
async def cmd_rules(message: types.Message):
    if message.chat.id != CHANNEL_ID:
        return
    
    rules = """📜 *ПРАВИЛА*

*🎰 Слот:*
7️⃣7️⃣7️⃣ = 5 NFT
Иначе = ❌ проигрыш

*🎲 Кубик:*
2 = 25 ⭐
4 = 50 ⭐
6 = 100 ⭐
Остальное = ❌

*Важно:*
• 30 секунд на ход
• Только под этим постом
• Одна попытка за раз"""
    
    await message.reply(rules)

# Команда /top
@dp.message_handler(commands=['top'])
async def cmd_top(message: types.Message):
    if message.chat.id != CHANNEL_ID:
        return
    
    await message.reply("🏆 Топ игроков пока пуст 🏆")

# Обработка сообщений 🎰 и 🎲
@dp.message_handler(lambda message: message.text in ['🎰', '🎲'])
async def handle_game(message: types.Message):
    if message.chat.id != CHANNEL_ID:
        return
    
    user = message.from_user
    game_type = 'slot' if message.text == '🎰' else 'dice'
    
    # Проверяем, есть ли уже активная игра
    active_game = db.get_game(user.id)
    
    if active_game:
        # Уже есть игра - говорим, что нужно подождать
        await message.reply(f"{EMOJI['fail']} У вас уже есть активная игра! Закончите её сначала.")
        return
    
    # Новая игра
    if game_type == 'slot':
        # Крутим слот
        await message.react([types.ReactionTypeEmoji(emoji="🎰")])
        
        if check_jackpot():
            # Выигрыш! Начинаем серию
            db.start_game(user.id, message.chat.id, message.message_id, game_type)
            db.update_game(user.id, stage='second_spin', first_jackpot=True)
            
            await message.reply(
                f"{EMOJI['fire']} *7️⃣7️⃣7️⃣ ДЖЕКПОТ!*\n\n"
                f"30 секунд, чтобы поймать *ВТОРОЙ* 7️⃣7️⃣7️⃣!\n"
                f"Отправь 🎰 ещё раз!"
            )
        else:
            # Проигрыш
            await message.reply(f"{EMOJI['slot']} Не повезло... Попробуй ещё!")
    
    else:  # Кубик
        msg = await message.reply_dice(emoji='🎲')
        await asyncio.sleep(2)  # Ждём анимацию
        
        dice_value = msg.dice.value
        prizes = {2: 25, 4: 50, 6: 100}
        
        if dice_value in prizes:
            prize = prizes[dice_value]
            db.add_win(user.id, 'stars', prize)
            emoji = {25: '🎁', 50: '🚀', 100: '💎'}[prize]
            
            await message.reply(
                f"{EMOJI['dice']} {dice_value}\n\n"
                f"{emoji} *ВЫИГРЫШ!* +{prize} ⭐"
            )
        else:
            await message.reply(f"{EMOJI['dice']} {dice_value}\n\n{EMOJI['fail']} Не повезло...")

# Запуск бота
if __name__ == "__main__":
    import time
    time.sleep(2)  # Небольшая задержка перед запуском
    print("Бот запускается...")
    try:
        executor.start_polling(dp, skip_updates=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)

