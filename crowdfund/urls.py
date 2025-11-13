from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from . import views
# Временная view для главной — пока нет apps/users/views.py:index
def index(request):
    return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('enter/', views.enter, name='enter'),
    path('forgotpass/', views.forgotpass, name='forgotpass'),
]