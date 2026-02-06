# projects/models_sql.py

from .database import db
from datetime import datetime
from decimal import Decimal
import bcrypt
import re

class User:
    @staticmethod
    def create(username, password, email=None, first_name='', last_name='', **kwargs):
        """Создание нового пользователя"""
        # Валидация пароля
        if len(password) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        query = """
            INSERT INTO users (
                username, password, email, first_name, last_name, 
                avatar, telegram, age, bio, city, crypto_wallet,
                is_active, is_staff, is_superuser, date_joined
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        params = (
            username, hashed_password, email, first_name, last_name,
            kwargs.get('avatar'), kwargs.get('telegram'), kwargs.get('age'),
            kwargs.get('bio'), kwargs.get('city'), kwargs.get('crypto_wallet'),
            True, False, False, datetime.now()
        )
        
        result = db.execute_query(query, params)
        user_id = result[0]['id']
        return User.get_by_id(user_id)
    
    @staticmethod
    def get_by_id(user_id):
        """Получение пользователя по ID"""
        query = "SELECT * FROM users WHERE id = %s AND is_active = TRUE"
        result = db.execute_query(query, (user_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_by_username(username):
        """Получение пользователя по имени"""
        query = "SELECT * FROM users WHERE username = %s AND is_active = TRUE"
        result = db.execute_query(query, (username,))
        return result[0] if result else None
    
    @staticmethod
    def get_by_email(email):
        """Получение пользователя по email"""
        query = "SELECT * FROM users WHERE email = %s AND is_active = TRUE"
        result = db.execute_query(query, (email,))
        return result[0] if result else None
    
    @staticmethod
    def authenticate(username, password):
        """Аутентификация пользователя"""
        # Сначала ищем по имени пользователя
        user = User.get_by_username(username)
        
        # Если не найден, пробуем по email
        if not user and '@' in username:
            user = User.get_by_email(username)
        
        if not user:
            return None
        
        # Проверяем пароль
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Обновляем время последнего входа
            db.execute_update(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.now(), user['id'])
            )
            return user
        return None
    
    @staticmethod
    def update(user_id, **kwargs):
        """Обновление данных пользователя"""
        fields = []
        params = []
        
        # Валидация и подготовка полей
        if 'username' in kwargs and kwargs['username']:
            fields.append("username = %s")
            params.append(kwargs['username'])
        
        if 'email' in kwargs:
            email = kwargs['email'].strip() if kwargs['email'] else None
            fields.append("email = %s")
            params.append(email)
        
        if 'first_name' in kwargs:
            fields.append("first_name = %s")
            params.append(kwargs['first_name'])
        
        if 'last_name' in kwargs:
            fields.append("last_name = %s")
            params.append(kwargs['last_name'])
        
        if 'avatar' in kwargs:
            fields.append("avatar = %s")
            params.append(kwargs['avatar'])
        
        if 'telegram' in kwargs:
            telegram = kwargs['telegram'].strip()
            # Нормализация Telegram: убираем @ в начале, добавляем обратно при сохранении
            if telegram.startswith('@'):
                telegram = telegram[1:]
            fields.append("telegram = %s")
            params.append(f'@{telegram}' if telegram else '')
        
        if 'age' in kwargs:
            age = kwargs['age']
            if age is not None and (not isinstance(age, int) or age < 1 or age > 150):
                raise ValueError("Возраст должен быть в диапазоне 1-150 лет")
            fields.append("age = %s")
            params.append(age)
        
        if 'bio' in kwargs:
            fields.append("bio = %s")
            params.append(kwargs['bio'])
        
        if 'city' in kwargs:
            fields.append("city = %s")
            params.append(kwargs['city'])
        
        if 'crypto_wallet' in kwargs:
            wallet = kwargs['crypto_wallet'].strip()
            # Базовая валидация кошелька (можно расширить)
            if wallet and not re.match(r'^[a-zA-Z0-9]{20,}$', wallet):
                raise ValueError("Некорректный формат крипто-кошелька")
            fields.append("crypto_wallet = %s")
            params.append(wallet if wallet else '')
        
        if 'password' in kwargs and kwargs['password']:
            if len(kwargs['password']) < 8:
                raise ValueError("Новый пароль должен содержать минимум 8 символов")
            hashed_password = bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            fields.append("password = %s")
            params.append(hashed_password)
        
        if not fields:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        return db.execute_update(query, params) > 0
    
    @staticmethod
    def delete(user_id):
        """Мягкое удаление пользователя (деактивация)"""
        query = "UPDATE users SET is_active = FALSE WHERE id = %s"
        return db.execute_update(query, (user_id,)) > 0


class Category:
    @staticmethod
    def get_all():
        """Получение всех категорий"""
        query = "SELECT * FROM categories ORDER BY name"
        return db.execute_query(query)
    
    @staticmethod
    def get_by_id(category_id):
        """Получение категории по ID"""
        query = "SELECT * FROM categories WHERE id = %s"
        result = db.execute_query(query, (category_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_by_slug(slug):
        """Получение категории по слагу"""
        query = "SELECT * FROM categories WHERE slug = %s"
        result = db.execute_query(query, (slug,))
        return result[0] if result else None


class Project:
    @staticmethod
    def create(owner_id, title, description, category_id, target_amount, deadline, 
               slogan='', image=None, status='draft'):
        """Создание нового проекта"""
        # Валидация данных
        if not title or len(title) < 3:
            raise ValueError("Название проекта должно содержать минимум 3 символа")
        
        if not description or len(description) < 20:
            raise ValueError("Описание проекта должно содержать минимум 20 символов")
        
        if Decimal(target_amount) <= 0:
            raise ValueError("Целевая сумма должна быть больше 0")
        
        if deadline <= datetime.now():
            raise ValueError("Дедлайн должен быть в будущем")
        
        query = """
            INSERT INTO projects (
                owner_id, title, slogan, description, category_id, 
                target_amount, collected_amount, image, deadline, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        params = (
            owner_id, title, slogan, description, category_id,
            Decimal(target_amount), Decimal('0.00'), image, deadline, status, datetime.now()
        )
        
        result = db.execute_query(query, params)
        project_id = result[0]['id']
        return Project.get_by_id(project_id)
    
    @staticmethod
    def get_by_id(project_id):
        """Получение проекта по ID с данными владельца и категории"""
        query = """
            SELECT 
                p.*, 
                u.username as owner_username, 
                u.avatar as owner_avatar,
                c.name as category_name,
                c.slug as category_slug,
                c.icon as category_icon,
                (p.deadline - NOW()) AS days_left_interval
            FROM projects p
            JOIN users u ON p.owner_id = u.id
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """
        result = db.execute_query(query, (project_id,))
        if not result:
            return None
        
        project = result[0]
        # Рассчитываем дни до дедлайна
        if project['days_left_interval']:
            project['days_left'] = max(0, project['days_left_interval'].days)
        else:
            project['days_left'] = 0
        
        return project
    
    @staticmethod
    def get_all(status=None, limit=20, offset=0):
        """Получение списка проектов"""
        query = """
            SELECT 
                p.*, 
                u.username as owner_username, 
                u.avatar as owner_avatar,
                c.name as category_name,
                c.slug as category_slug,
                c.icon as category_icon,
                (p.deadline - NOW()) AS days_left_interval
            FROM projects p
            JOIN users u ON p.owner_id = u.id
            JOIN categories c ON p.category_id = c.id
            WHERE p.status != 'draft'
        """
        params = []
        
        if status:
            query += " AND p.status = %s"
            params.append(status)
        
        query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = db.execute_query(query, params)
        
        # Нормализуем дни до дедлайна
        for project in results:
            if project['days_left_interval']:
                project['days_left'] = max(0, project['days_left_interval'].days)
            else:
                project['days_left'] = 0
        
        return results
    
    @staticmethod
    def get_by_owner(owner_id, status=None):
        """Получение проектов пользователя"""
        query = """
            SELECT 
                p.*, 
                c.name as category_name,
                c.slug as category_slug,
                c.icon as category_icon,
                (p.deadline - NOW()) AS days_left_interval
            FROM projects p
            JOIN categories c ON p.category_id = c.id
            WHERE p.owner_id = %s
        """
        params = [owner_id]
        
        if status:
            query += " AND p.status = %s"
            params.append(status)
        
        query += " ORDER BY p.created_at DESC"
        
        results = db.execute_query(query, params)
        
        # Нормализуем дни до дедлайна
        for project in results:
            if project['days_left_interval']:
                project['days_left'] = max(0, project['days_left_interval'].days)
            else:
                project['days_left'] = 0
        
        return results
    
    @staticmethod
    def update(project_id, **kwargs):
        """Обновление проекта"""
        fields = []
        params = []
        
        if 'title' in kwargs and kwargs['title']:
            fields.append("title = %s")
            params.append(kwargs['title'])
        
        if 'slogan' in kwargs:
            fields.append("slogan = %s")
            params.append(kwargs['slogan'])
        
        if 'description' in kwargs and kwargs['description']:
            fields.append("description = %s")
            params.append(kwargs['description'])
        
        if 'category_id' in kwargs:
            fields.append("category_id = %s")
            params.append(kwargs['category_id'])
        
        if 'target_amount' in kwargs:
            amount = Decimal(kwargs['target_amount'])
            if amount <= 0:
                raise ValueError("Целевая сумма должна быть больше 0")
            fields.append("target_amount = %s")
            params.append(amount)
        
        if 'image' in kwargs:
            fields.append("image = %s")
            params.append(kwargs['image'])
        
        if 'deadline' in kwargs:
            deadline = kwargs['deadline']
            if deadline <= datetime.now():
                raise ValueError("Дедлайн должен быть в будущем")
            fields.append("deadline = %s")
            params.append(deadline)
        
        if 'status' in kwargs:
            valid_statuses = ['draft', 'active', 'success', 'expired']
            if kwargs['status'] not in valid_statuses:
                raise ValueError(f"Неверный статус. Допустимые значения: {', '.join(valid_statuses)}")
            fields.append("status = %s")
            params.append(kwargs['status'])
        
        if not fields:
            return False
        
        params.append(project_id)
        query = f"UPDATE projects SET {', '.join(fields)} WHERE id = %s"
        return db.execute_update(query, params) > 0
    
    @staticmethod
    def update_collected_amount(project_id, amount):
        """Обновление собранной суммы"""
        query = "UPDATE projects SET collected_amount = collected_amount + %s WHERE id = %s"
        return db.execute_update(query, (Decimal(amount), project_id)) > 0
    
    @staticmethod
    def update_status(project_id):
        """Обновление статуса проекта на основе текущих данных"""
        query = """
            UPDATE projects 
            SET status = CASE 
                WHEN collected_amount >= target_amount AND deadline > NOW() THEN 'success'
                WHEN deadline <= NOW() AND collected_amount < target_amount THEN 'expired'
                WHEN deadline > NOW() AND collected_amount < target_amount THEN 'active'
                ELSE status
            END
            WHERE id = %s
        """
        return db.execute_update(query, (project_id,))
    
    @staticmethod
    def delete(project_id):
        """Удаление проекта (каскадное удаление пожертвований произойдет автоматически)"""
        query = "DELETE FROM projects WHERE id = %s"
        return db.execute_update(query, (project_id,)) > 0


class Donation:
    @staticmethod
    def create(project_id, amount, currency, amount_usdt_equivalent, 
               donor_id=None, email_receipt='', bitpay_invoice_id=None, 
               bitpay_status='pending', is_anonymous=False):
        """Создание нового пожертвования"""
        # Валидация суммы
        amount_dec = Decimal(amount)
        usdt_dec = Decimal(amount_usdt_equivalent)
        
        if amount_dec <= 0:
            raise ValueError("Сумма пожертвования должна быть больше 0")
        
        if usdt_dec <= 0:
            raise ValueError("Эквивалент в USDT должен быть больше 0")
        
        # Валидация валюты
        valid_currencies = ['BTC', 'ETH', 'USDT_TRC20', 'USDT_ERC20']
        if currency not in valid_currencies:
            raise ValueError(f"Неверная валюта. Допустимые значения: {', '.join(valid_currencies)}")
        
        query = """
            INSERT INTO donations (
                project_id, donor_id, amount, amount_usdt_equivalent, currency,
                email_receipt, bitpay_invoice_id, bitpay_status, is_anonymous, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        params = (
            project_id, donor_id, amount_dec, usdt_dec, currency,
            email_receipt, bitpay_invoice_id, bitpay_status, is_anonymous, datetime.now()
        )
        
        result = db.execute_query(query, params)
        donation_id = result[0]['id']
        
        # Обновляем собранную сумму проекта
        Project.update_collected_amount(project_id, usdt_dec)
        Project.update_status(project_id)
        
        return Donation.get_by_id(donation_id)
    
    @staticmethod
    def get_by_id(donation_id):
        """Получение пожертвования по ID"""
        query = """
            SELECT 
                d.*, 
                p.title as project_title,
                p.image as project_image,
                CASE 
                    WHEN d.is_anonymous OR d.donor_id IS NULL THEN 'Аноним'
                    ELSE u.username 
                END as donor_name,
                u.avatar as donor_avatar
            FROM donations d
            JOIN projects p ON d.project_id = p.id
            LEFT JOIN users u ON d.donor_id = u.id
            WHERE d.id = %s
        """
        result = db.execute_query(query, (donation_id,))
        return result[0] if result else None
    
    @staticmethod
    def get_by_project(project_id, limit=50, offset=0):
        """Получение пожертвований проекта"""
        query = """
            SELECT 
                d.*,
                CASE 
                    WHEN d.is_anonymous OR d.donor_id IS NULL THEN 'Аноним'
                    ELSE u.username 
                END as donor_name,
                u.avatar as donor_avatar
            FROM donations d
            LEFT JOIN users u ON d.donor_id = u.id
            WHERE d.project_id = %s
            ORDER BY d.created_at DESC
            LIMIT %s OFFSET %s
        """
        return db.execute_query(query, (project_id, limit, offset))
    
    @staticmethod
    def get_by_donor(donor_id, limit=50, offset=0):
        """Получение пожертвований пользователя"""
        query = """
            SELECT 
                d.*, 
                p.title as project_title,
                p.image as project_image,
                p.owner_id as project_owner_id
            FROM donations d
            JOIN projects p ON d.project_id = p.id
            WHERE d.donor_id = %s AND d.is_anonymous = FALSE
            ORDER BY d.created_at DESC
            LIMIT %s OFFSET %s
        """
        return db.execute_query(query, (donor_id, limit, offset))
    
    @staticmethod
    def update_bitpay_status(donation_id, status):
        """Обновление статуса платежа"""
        valid_statuses = ['new', 'paid', 'confirmed', 'complete', 'expired', 'invalid']
        if status not in valid_statuses:
            raise ValueError(f"Неверный статус BitPay. Допустимые значения: {', '.join(valid_statuses)}")
        
        query = "UPDATE donations SET bitpay_status = %s WHERE id = %s"
        return db.execute_update(query, (status, donation_id)) > 0
    
    @staticmethod
    def rollback_donation(donation_id):
        """Откат пожертвования при неудачной оплате"""
        donation = Donation.get_by_id(donation_id)
        if not donation:
            return False
        
        # Уменьшаем собранную сумму проекта
        query = """
            UPDATE projects 
            SET collected_amount = GREATEST(0, collected_amount - %s) 
            WHERE id = %s
        """
        db.execute_update(query, (donation['amount_usdt_equivalent'], donation['project_id']))
        
        # Обновляем статус проекта
        Project.update_status(donation['project_id'])
        
        return True