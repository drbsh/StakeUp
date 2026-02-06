# projects/database.py

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

class Database:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'stakeup_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'drbsh'),
            'port': os.getenv('DB_PORT', '5432')
        }
        self.connection = None
    
    def connect(self):
        """Подключение к базе данных"""
        if self.connection and not self.connection.closed:
            return self.connection
        
        try:
            self.connection = psycopg2.connect(**self.config)
            return self.connection
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            raise
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def get_cursor(self):
        """Контекстный менеджер для работы с курсором"""
        conn = self.connect()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"❌ Ошибка выполнения запроса: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query, params=None):
        """Выполнение SELECT запроса"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    def execute_update(self, query, params=None):
        """Выполнение запроса на изменение данных (INSERT/UPDATE/DELETE)"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount
    
    def execute_insert(self, query, params=None):
        """Выполнение запроса на вставку с возвратом последнего ID"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            # Для PostgreSQL с SERIAL возвращаем последний вставленный ID
            cursor.execute("SELECT LASTVAL();")
            return cursor.fetchone()['lastval']

# Глобальный экземпляр базы данных
db = Database()