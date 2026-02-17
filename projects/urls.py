# projects/urls.py

from django.urls import path
from . import views_sql

app_name = 'projects'

urlpatterns = [
    
    path('api/forgot-password/', views_sql.api_forgot_password, name='api_forgot_password'),  # ← добавить
    path('api/reset-password/', views_sql.api_reset_password, name='api_reset_password'), 
    
    # Основные страницы
    path('', views_sql.index, name='index'),
    path('about/', views_sql.about, name='about'),
    path('projects/', views_sql.projects_list, name='projects_list'),
    path('projects/<int:project_id>/', views_sql.project_detail, name='project_detail'),
    
    # Авторизация - страницы
    path('register/', views_sql.register, name='register'),
    path('login/', views_sql.login_view, name='login'),
    path('enter/', views_sql.login_view, name='enter'),  # ← ДОБАВЛЕНО для совместимости
    path('forgot-password/', views_sql.forgot_password, name='forgot_password'),
    path('logout/', views_sql.logout_view, name='logout'),
    
        
    path('profile/', views_sql.profile, name='profile'),
    path('edit-profile/', views_sql.edit_profile, name='edit_profile'),
    path('delete-profile/', views_sql.delete_profile, name='delete_profile'),
    
    # Профиль и проекты
    path('profile/', views_sql.profile, name='profile'),
    path('create-project/', views_sql.create_project, name='create_project'),
    path('edit-profile/', views_sql.edit_profile, name='edit_profile'),
    
    # Пожертвования
    path('donate/<int:project_id>/', views_sql.donate, name='donate'),
    path('donate-process/', views_sql.donate_process, name='donate_process'),
    
    # Webhook от BitPay
    path('webhook/bitpay/', views_sql.bitpay_webhook, name='bitpay_webhook'),
]