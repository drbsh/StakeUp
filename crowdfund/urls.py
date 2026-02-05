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
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('projects/', views.projects, name='projects'),
    path('project_info/', views.project_info, name='project_info'),
    path('create_project/', views.create_project, name='create_project'),
    path('donate/', views.donate, name='donate'),
]