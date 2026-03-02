import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHANNEL_ID = int(os.environ.get('CHANNEL_ID', 0))

MOVE_TIMEOUT = 30
JACKPOT_CHANCE = 5
