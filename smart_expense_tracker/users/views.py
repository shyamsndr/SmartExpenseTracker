from django.shortcuts import render

def login_view(request):
    return render(request, 'pages-sign-in.html')

def register_view(request):
    return render(request, 'pages-sign-up.html')

def index(request):
    return render(request, 'index.html') 

def logout_view(request):
    return render(request, 'logout.html')

def blankpage_view(request):
    return render(request, 'pages-blank.html')