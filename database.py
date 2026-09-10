import sqlite3
from datetime import datetime
import os

DB_PATH = 'crm.db'

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица рабочих смен
    c.execute('''
        CREATE TABLE IF NOT EXISTS shifts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Таблица клиентов
    c.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            status TEXT DEFAULT 'available',
            assigned_to INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(assigned_to) REFERENCES users(id)
        )
    ''')
    
    # Таблица комментариев
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            client_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(client_id) REFERENCES clients(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user(username):
    """Получить пользователя по имени"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, password FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    return result

def add_user(username, password):
    """Добавить нового пользователя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def delete_user(user_id):
    """Удалить пользователя"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    """Получить всех пользователей"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, username, created_at FROM users')
    results = c.fetchall()
    conn.close()
    return results

def start_shift(user_id):
    """Начать рабочую смену"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO shifts (user_id, start_time) VALUES (?, ?)', (user_id, datetime.now()))
    conn.commit()
    shift_id = c.lastrowid
    conn.close()
    return shift_id

def end_shift(user_id):
    """Закончить рабочую смену"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE shifts SET end_time = ? WHERE user_id = ? AND end_time IS NULL', (datetime.now(), user_id))
    conn.commit()
    conn.close()

def get_current_shift(user_id):
    """Получить текущую смену"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, start_time FROM shifts WHERE user_id = ? AND end_time IS NULL', (user_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_shift_duration(user_id):
    """Получить длительность текущей смены в минутах"""
    shift = get_current_shift(user_id)
    if not shift:
        return 0
    start_time = datetime.fromisoformat(shift[1])
    duration = (datetime.now() - start_time).total_seconds() / 60
    return int(duration)

def add_client(name, phone, email):
    """Добавить клиента"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO clients (name, phone, email, status) VALUES (?, ?, ?, ?)', 
              (name, phone, email, 'available'))
    conn.commit()
    client_id = c.lastrowid
    conn.close()
    return client_id

def get_available_clients():
    """Получить доступных клиентов (не в работе)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, phone, email FROM clients WHERE status = "available" LIMIT 1')
    result = c.fetchone()
    conn.close()
    return result

def get_working_clients(user_id):
    """Получить клиентов в работе у пользователя"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name, phone, email FROM clients WHERE status = "working" AND assigned_to = ?', (user_id,))
    results = c.fetchall()
    conn.close()
    return results

def assign_client(client_id, user_id):
    """Назначить клиента пользователю"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE clients SET status = ?, assigned_to = ? WHERE id = ?', 
              ('working', user_id, client_id))
    conn.commit()
    conn.close()

def delete_client(client_id):
    """Удалить клиента"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()

def add_comment(client_id, user_id, comment):
    """Добавить комментарий"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO comments (client_id, user_id, comment) VALUES (?, ?, ?)', 
              (client_id, user_id, comment))
    conn.commit()
    conn.close()

def get_comments(client_id):
    """Получить комментарии к клиенту"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT user_id, comment, created_at FROM comments WHERE client_id = ? ORDER BY created_at DESC', (client_id,))
    results = c.fetchall()
    conn.close()
    return results

def get_username(user_id):
    """Получить имя пользователя по ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 'Unknown'
