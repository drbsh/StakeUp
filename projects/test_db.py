# test_db.py
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdfund.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from projects.database import db

try:
    # Проверяем подключение
    db.connect()
    print("✅ Подключение к базе данных успешно!")
    
    # Проверяем наличие таблиц
    tables = db.execute_query("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('users', 'categories', 'projects', 'donations')
    """)
    
    print(f"✅ Найдено таблиц: {len(tables)}")
    for table in tables:
        print(f"   - {table['table_name']}")
    
    db.disconnect()
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()