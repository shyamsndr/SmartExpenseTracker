from django.shortcuts import render,  redirect
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse

def login_view(request):
    return render(request, 'pages-sign-in.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validation
        if password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email is already registered.'})

        # Hash the password before saving (for security)
        hashed_password = make_password(password)

        # Save new user to database
        new_user = User(email=email, password=hashed_password)
        new_user.save()

        # Return success with redirection URL
        # Return success with redirection URL
        return JsonResponse({'status': 'success', 'message': 'Registration successful!', 'redirect_url': '/'})

    
    return render(request, 'pages-sign-up.html')

def index(request):
    return render(request, 'index.html') 

def logout_view(request):
    return render(request, 'logout.html')

def blankpage_view(request):
    return render(request, 'pages-blank.html')