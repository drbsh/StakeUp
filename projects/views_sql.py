# projects/views_sql.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json
import jwt
import datetime
import os  # ← КРИТИЧЕСКИ ВАЖНО: добавлен импорт os
from decimal import Decimal
from django.conf import settings  # ← Уже есть, но убедимся
from django.core.files.storage import default_storage  # ← ДОБАВЛЕНО
from .models_sql import User, Project, Category, Donation
from .database import db

# Настройки JWT
JWT_SECRET_KEY = 'change-this-in-production'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DAYS = 7

def generate_jwt_token(user_id, username):
    """Генерация JWT токена"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=JWT_EXPIRATION_DAYS),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token):
    """Верификация JWT токена"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Вспомогательная функция для получения данных пользователя
def get_user_data(request):
    """Получение данных пользователя для шаблонов"""
    if request.session.get('user_id'):
        user = User.get_by_id(request.session['user_id'])
        if user:
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'avatar': user['avatar'] if user['avatar'] else '/static/Image/default-avatar.png',
                'telegram': user['telegram'],
                'city': user['city'],
            }
    return None

# Базовые страницы
def index(request):
    print(f"DEBUG: session keys = {request.session.keys()}")
    print(f"DEBUG: session user_id = {request.session.get('user_id')}")
    print(f"DEBUG: session username = {request.session.get('username')}")

    projects = Project.get_all(status='active', limit=12)
    user_data = get_user_data(request)
    return render(request, 'index.html', {'projects': projects, 'user': user_data})

def about(request):
    user_data = get_user_data(request)
    return render(request, 'about.html', {'user': user_data})

def projects_list(request):
    status = request.GET.get('status', 'active')
    valid_statuses = ['active', 'success', 'expired']
    if status not in valid_statuses:
        status = 'active'
    
    projects = Project.get_all(status=status, limit=24)
    user_data = get_user_data(request)
    return render(request, 'projects.html', {'projects': projects, 'current_status': status, 'user': user_data})

def project_detail(request, project_id):
    project = Project.get_by_id(project_id)
    if not project:
        messages.error(request, 'Проект не найден')
        return redirect('projects:index')
    
    donations = Donation.get_by_project(project_id, limit=20)
    user_data = get_user_data(request)
    return render(request, 'project_info.html', {'project': project, 'donations': donations, 'user': user_data})

def register(request):
    user_data = get_user_data(request)
    return render(request, 'register.html', {'user': user_data})

def login_view(request):
    user_data = get_user_data(request)
    return render(request, 'enter.html', {'user': user_data})

def forgot_password(request):
    user_data = get_user_data(request)
    return render(request, 'forgotpass.html', {'user': user_data})

def logout_view(request):
    request.session.flush()
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('projects:index')

def profile(request):
    if not request.session.get('user_id'):
        messages.warning(request, 'Пожалуйста, войдите в систему')
        return redirect('projects:login')
    
    user_id = request.session['user_id']
    user = User.get_by_id(user_id)
    if not user:
        request.session.flush()
        messages.error(request, 'Пользователь не найден')
        return redirect('projects:login')
    
    projects = Project.get_by_owner(user_id)
    donations = Donation.get_by_donor(user_id)
    
    return render(request, 'profile.html', {
        'user': user,
        'projects': projects,
        'donations': donations
    })

# API эндпоинты
@api_view(['POST'])
@permission_classes([AllowAny])
def api_forgot_password(request):
    """
    Заглушка: генерация токена сброса пароля
    В реальном проекте: отправка email с ссылкой для сброса
    """
    identifier = request.data.get('identifier')  # логин или email
    
    if not identifier:
        return Response(
            {'detail': 'Укажите логин или email'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'uid': 'MTIz',  # base64-encoded "123"
        'token': '5x-3y-9z-test-token',
        'detail': 'Ссылка для сброса пароля отправлена на ваш email (заглушка)'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_reset_password(request):
    """
    Заглушка: сброс пароля по токену
    """
    uid = request.data.get('uid')
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    
    # Валидация
    if not all([uid, token, new_password, confirm_password]):
        return Response(
            {'detail': 'Все поля обязательны'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if new_password != confirm_password:
        return Response(
            {'detail': 'Пароли не совпадают'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(new_password) < 8:
        return Response(
            {'detail': 'Пароль должен содержать минимум 8 символов'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'detail': 'Пароль успешно изменён! (заглушка)'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username') or request.data.get('email')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'detail': 'Требуются логин/почта и пароль'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.authenticate(username, password)
    
    if user:
        token = generate_jwt_token(user['id'], user['username'])
        
        # Сохраняем данные в сессию Django
        request.session['user_id'] = user['id']
        request.session['username'] = user['username']
        
        # Возвращаем данные для фронтенда
        return Response({
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'avatar': user['avatar'] if user['avatar'] else '/static/Image/default-avatar.png',
                'telegram': user['telegram'],
                'city': user['city']
            },
            'token': token,
            'detail': 'Успешная аутентификация'
        })
    
    return Response(
        {'detail': 'Неверные учётные данные'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')
    
    if not username or not password:
        return Response(
            {'detail': 'Требуются имя пользователя и пароль'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 8:
        return Response(
            {'detail': 'Пароль должен содержать минимум 8 символов'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.get_by_username(username):
        return Response(
            {'detail': 'Пользователь с таким именем уже существует'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if email and User.get_by_email(email):
        return Response(
            {'detail': 'Пользователь с таким email уже существует'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.create(
            username=username,
            password=password,
            email=email if email else None,
        )
    except Exception as e:
        return Response(
            {'detail': f'Ошибка создания пользователя: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    token = generate_jwt_token(user['id'], user['username'])
    
    # Сохраняем данные в сессию Django
    request.session['user_id'] = user['id']
    request.session['username'] = user['username']
    
    return Response({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'avatar': user['avatar'] if user['avatar'] else '/static/Image/default-avatar.png',
        },
        'token': token,
        'detail': 'Регистрация успешна'
    }, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    auth_header = request.headers.get('Authorization', '')
    user_id = None
    
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        payload = verify_jwt_token(token)
        if payload:
            user_id = payload.get('user_id')
    
    if not user_id and request.session.get('user_id'):
        user_id = request.session['user_id']
    
    if not user_id:
        return Response(
            {'detail': 'Не авторизован'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = User.get_by_id(user_id)
    if not user:
        return Response(
            {'detail': 'Пользователь не найден'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        return Response({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'telegram': user['telegram'],
            'age': user['age'],
            'city': user['city'],
            'bio': user['bio'],
            'crypto_wallet': user['crypto_wallet'],
            'avatar': user['avatar']
        })
    
    elif request.method == 'PATCH':
        update_data = {}
        
        fields_map = {
            'email': 'email',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'telegram': 'telegram',
            'age': 'age',
            'city': 'city',
            'bio': 'bio',
            'crypto_wallet': 'crypto_wallet',
            'password': 'password'
        }
        
        for field, db_field in fields_map.items():
            if field in request.data:
                update_data[db_field] = request.data[field]
        
        try:
            if update_data:
                User.update(user_id, **update_data)
                user = User.get_by_id(user_id)
            
            return Response({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name'],
                'telegram': user['telegram'],
                'age': user['age'],
                'city': user['city'],
                'bio': user['bio'],
                'crypto_wallet': user['crypto_wallet'],
                'avatar': user['avatar']
            })
        except ValueError as e:
            return Response(
                {'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'detail': f'Ошибка обновления: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# Удаление профиля
def delete_profile(request):
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Необходимо войти в систему'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Неверный метод запроса'}, status=405)
    
    try:
        user_id = request.session['user_id']
        user = User.get_by_id(user_id)
        
        if not user:
            request.session.flush()
            return JsonResponse({'error': 'Пользователь не найден'}, status=404)
        
        # 🔥 ВАЖНО: Проверяем, есть ли активные проекты
        active_projects = Project.get_by_owner(user_id, status='active')
        if active_projects:
            return JsonResponse({
                'error': f'У вас есть {len(active_projects)} активных проектов. Сначала удалите или завершите их.',
                'active_projects_count': len(active_projects)
            }, status=400)
        
        # 🔥 Удаляем все проекты пользователя (включая черновики)
        projects = Project.get_by_owner(user_id)
        for project in projects:
            Project.delete(project['id'])
        
        # 🔥 Удаляем все пожертвования пользователя
        donations = Donation.get_by_donor(user_id)
        for donation in donations:
            Donation.rollback_donation(donation['id'])
        
        # 🔥 Удаляем аватар из файловой системы
        if user['avatar'] and not user['avatar'].startswith('/static/'):
            try:
                avatar_path = os.path.join(settings.MEDIA_ROOT, user['avatar'].lstrip('/media/').lstrip('/'))
                if os.path.exists(avatar_path):
                    os.remove(avatar_path)
            except Exception as e:
                print(f"⚠️ Ошибка при удалении аватара: {e}")
        
        # 🔥 Мягкое удаление пользователя (деактивация)
        User.delete(user_id)
        
        # 🔥 Очищаем сессию
        request.session.flush()
        
        return JsonResponse({
            'success': True,
            'message': 'Ваш профиль успешно удалён. Спасибо за использование платформы!'
        }, status=200)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': f'Ошибка при удалении профиля: {str(e)}'
        }, status=500)

# Создание проекта
def create_project(request):
    if not request.session.get('user_id'):
        messages.warning(request, 'Пожалуйста, войдите в систему для создания проекта')
        return redirect('projects:login')
    
    if request.method == 'POST':
        user_id = request.session['user_id']
        title = request.POST.get('title', '').strip()
        slogan = request.POST.get('slogan', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        target_amount = request.POST.get('target_amount', '0')
        deadline_str = request.POST.get('deadline')
        
        try:
            if not category_id or not category_id.isdigit():
                raise ValueError("Выберите категорию проекта")
            
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
            
            project = Project.create(
                owner_id=user_id,
                title=title,
                description=description,
                category_id=int(category_id),
                target_amount=target_amount,
                deadline=deadline,
                slogan=slogan,
                status='draft'
            )
            
            messages.success(request, '✅ Проект успешно создан и сохранён в черновиках!')
            return redirect('projects:profile')
            
        except Exception as e:
            messages.error(request, f'❌ Ошибка при создании проекта: {str(e)}')
            return redirect('projects:create_project')
    
    categories = Category.get_all()
    user_data = get_user_data(request)
    return render(request, 'create_project.html', {'categories': categories, 'user': user_data})

# Редактирование профиля
# Редактирование профиля
def edit_profile(request):
    if not request.session.get('user_id'):
        return redirect('projects:login')
    
    user_id = request.session['user_id']
    user = User.get_by_id(user_id)
    if not user:
        request.session.flush()
        return redirect('projects:login')
    
    if request.method == 'POST':
        try:
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            age_value = request.POST.get('age', '').strip()
            city = request.POST.get('city', '').strip()
            telegram = request.POST.get('telegram', '').strip()
            bio = request.POST.get('bio', '').strip()
            crypto_wallet = request.POST.get('crypto_wallet', '').strip()
            
            first_name, last_name = '', ''
            if full_name:
                parts = full_name.split(' ', 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''
            
            age = int(age_value) if age_value.isdigit() and 1 <= int(age_value) <= 150 else None
            
            update_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email if email else None,
                'age': age,
                'city': city,
                'telegram': telegram,
                'bio': bio,
                'crypto_wallet': crypto_wallet
            }
            
            # 🔥 ОБРАБОТКА ЗАГРУЗКИ АВАТАРА
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                
                # Валидация файла
                if avatar_file.size > 5 * 1024 * 1024:  # 5 МБ
                    raise ValueError("Размер файла не должен превышать 5 МБ")
                
                # Разрешённые расширения
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
                ext = os.path.splitext(avatar_file.name)[1].lower()
                if ext not in allowed_extensions:
                    raise ValueError("Разрешены только файлы форматов JPG, JPEG, PNG, GIF")
                
                # Удаляем старый аватар, если он есть
                if user['avatar'] and user['avatar'] != '/static/image/default-avatar.png':
                    old_avatar_path = os.path.join(settings.MEDIA_ROOT, user['avatar'].lstrip('/media/').lstrip('/'))
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                
                # Генерируем новое имя файла
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"avatar_{user_id}_{timestamp}{ext}"
                filepath = os.path.join('avatars', filename)
                
                # Сохраняем файл
                full_path = default_storage.save(filepath, avatar_file)
                
                # Сохраняем путь в БД (относительный путь от MEDIA_ROOT)
                update_data['avatar'] = f'/media/{full_path}'
            
            # Обновляем пользователя
            User.update(user_id, **update_data)
            
            # Обновляем данные в сессии
            updated_user = User.get_by_id(user_id)
            request.session['username'] = updated_user['username']
            
            messages.success(request, '✅ Профиль успешно обновлён!')
            return redirect('projects:profile')
            
        except ValueError as e:
            messages.error(request, f'⚠️ Ошибка валидации: {str(e)}')
        except Exception as e:
            messages.error(request, f'❌ Ошибка при сохранении: {str(e)}')
            import traceback
            traceback.print_exc()
    
    # GET запрос - показываем форму
    telegram_for_form = user['telegram'].replace('@', '') if user['telegram'] else ''
    user_data = get_user_data(request)
    
    return render(request, 'edit_profile.html', {
        'user': user,
        'telegram_for_form': telegram_for_form,
        'user_data': user_data
    })

# Пожертвования
def donate(request, project_id):
    if not request.session.get('user_id'):
        messages.warning(request, 'Пожалуйста, войдите в систему для совершения пожертвования')
        return redirect('projects:login')
    
    project = Project.get_by_id(project_id)
    if not project:
        messages.error(request, 'Проект не найден')
        return redirect('projects:index')
    
    if project['status'] not in ['active', 'draft']:
        messages.warning(request, 'Пожертвования для этого проекта недоступны')
        return redirect('projects:project_detail', project_id=project_id)
    
    user_data = get_user_data(request)
    return render(request, 'donate.html', {'project': project, 'user': user_data})

def donate_process(request):
    if not request.session.get('user_id'):
        return JsonResponse({'error': 'Необходимо войти в систему'}, status=401)
    
    if request.method != 'POST':
        return redirect('projects:index')
    
    try:
        user_id = request.session['user_id']
        project_id = int(request.POST.get('project_id'))
        amount = Decimal(request.POST.get('amount'))
        currency = request.POST.get('currency')
        email = request.POST.get('email', '').strip()
        is_anonymous = request.POST.get('is_anonymous') == 'on'
        
        project = Project.get_by_id(project_id)
        if not project:
            raise ValueError('Проект не найден')
        
        if project['status'] not in ['active', 'draft']:
            raise ValueError('Пожертвования для этого проекта недоступны')
        
        amount_usdt = amount
        if currency == 'BTC':
            amount_usdt = amount * Decimal('50000')
        elif currency == 'ETH':
            amount_usdt = amount * Decimal('3000')
        
        donor_id = None if is_anonymous else user_id
        donation = Donation.create(
            project_id=project_id,
            amount=amount,
            currency=currency,
            amount_usdt_equivalent=amount_usdt,
            donor_id=donor_id,
            email_receipt=email,
            bitpay_status='new'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Платёж успешно обработан! Спасибо за поддержку проекта.',
            'donation_id': donation['id'],
            'redirect_url': f"/projects/{project_id}/"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при обработке платежа: {str(e)}'
        }, status=400)

# BitPay Webhook
@csrf_exempt
def bitpay_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    try:
        payload = json.loads(request.body)
        invoice_id = payload.get('id')
        status = payload.get('status')
        
        if not invoice_id or not status:
            return HttpResponse('Invalid payload', status=400)
        
        query = "SELECT * FROM donations WHERE bitpay_invoice_id = %s"
        result = db.execute_query(query, (invoice_id,))
        
        if not result:
            return HttpResponse('Donation not found', status=404)
        
        donation = result[0]
        
        Donation.update_bitpay_status(donation['id'], status)
        
        if status in ('failed', 'expired', 'invalid'):
            Donation.rollback_donation(donation['id'])
        elif status in ('confirmed', 'complete'):
            Project.update_status(donation['project_id'])
        
        return HttpResponse('OK', status=200)
        
    except json.JSONDecodeError:
        return HttpResponse('Invalid JSON', status=400)
    except Exception as e:
        print(f"❌ Ошибка вебхука BitPay: {e}")
        return HttpResponse(f'Internal error: {str(e)}', status=500)