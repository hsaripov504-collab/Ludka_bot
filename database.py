import sqlite3
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name="games.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance_stars INTEGER DEFAULT 0,
                nft_count INTEGER DEFAULT 0,
                games_played INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS active_games (
                user_id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                message_id INTEGER,
                stage TEXT,
                game_type TEXT,
                deadline TIMESTAMP,
                first_jackpot BOOLEAN DEFAULT 0,
                second_jackpot BOOLEAN DEFAULT 0
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                game_type TEXT,
                result TEXT,
                prize TEXT,
                timestamp TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()
    
    def create_user(self, user_id, username, first_name):
        self.cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))
        self.conn.commit()
    
    def start_game(self, user_id, chat_id, message_id, game_type):
        self.cursor.execute("DELETE FROM active_games WHERE user_id = ?", (user_id,))
        deadline = datetime.now() + timedelta(seconds=30)
        self.cursor.execute("""
            INSERT INTO active_games (user_id, chat_id, message_id, stage, game_type, deadline)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, chat_id, message_id, 'first_spin', game_type, deadline))
        self.conn.commit()
    
    def update_game(self, user_id, **kwargs):
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(user_id)
        
        query = f"UPDATE active_games SET {', '.join(fields)} WHERE user_id = ?"
        self.cursor.execute(query, values)
        self.conn.commit()
    
    def get_game(self, user_id):
        self.cursor.execute("SELECT * FROM active_games WHERE user_id = ?", (user_id,))
        return self.cursor.fetchone()
    
    def end_game(self, user_id):
        self.cursor.execute("DELETE FROM active_games WHERE user_id = ?", (user_id,))
        self.conn.commit()
    
    def add_win(self, user_id, prize_type, prize_value):
        if prize_type == "stars":
            self.cursor.execute("""
                UPDATE users SET balance_stars = balance_stars + ?, wins = wins + 1
                WHERE user_id = ?
            """, (prize_value, user_id))
        elif prize_type == "nft":
            self.cursor.execute("""
                UPDATE users SET nft_count = nft_count + 1, wins = wins + 1
                WHERE user_id = ?
            """, (user_id,))
        
        self.cursor.execute("""
            INSERT INTO game_history (user_id, game_type, result, prize, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, prize_type, str(prize_value), str(prize_value), datetime.now()))
        self.conn.commit()
