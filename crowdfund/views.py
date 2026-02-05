from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def register(request):  
    return render(request, 'register.html')  

def enter(request):  
    return render(request, 'enter.html')  
def forgotpass(request):  
    return render(request, 'forgotpass.html')  
def profile(request):  
    return render(request, 'profile.html')
def edit_profile(request):  
    return render(request, 'edit_profile.html')
def projects(request):  
    return render(request, 'projects.html')
def project_info(request):  
    return render(request, 'project_info.html')
def create_project(request):  
    return render(request, 'create_project.html')
def donate(request):  
    return render(request, 'donate.html')