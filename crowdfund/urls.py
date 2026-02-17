# crowdfund/urls.py

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from projects import views_sql

urlpatterns = [
    # API эндпоинты
    path('api/register/', views_sql.api_register, name='api_register'),
    path('api/login/', views_sql.api_login, name='api_login'),
    path('api/profile/', views_sql.api_profile, name='api_profile'),
    path('api/forgot-password/', views_sql.api_forgot_password, name='api_forgot_password'),  # ← ДОБАВЛЕНО
    path('api/reset-password/', views_sql.api_reset_password, name='api_reset_password'), 
    
    # Все остальные маршруты из приложения projects
    path('', include('projects.urls', namespace='projects')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)