from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):  # Compare with the hashed password
                request.session['user_id'] = user.u_id  # Store user ID in session
                messages.success(request, "Logged in successfully!")
                return redirect('index')  # Redirect to the home page after login
            else:
                messages.error(request, "Invalid password.")
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")

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

        # Hash the password before saving
        hashed_password = make_password(password)

        # Save new user
        new_user = User(email=email, password=hashed_password)
        new_user.save()

        return JsonResponse({'status': 'success', 'message': 'Registration successful!', 'redirect_url': '/'})

    return render(request, 'pages-sign-up.html')


def index(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if not authenticated
    return render(request, 'index.html')


def logout_view(request):
    # Clear user session on logout
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('login')

def transactions_view(request):
    return render(request, 'transactions.html')

def expense_page(request):
    return render(request, "expense.html")

def manage_categories_page(request):
    return render(request, "manage_categories.html")

def manage_payment_methods_page(request):
    return render(request, "manage_payment_methods.html")

def manage_source_of_income(request):
    return render(request, 'manage_source_of_income.html')

def budget_management(request):
    return render(request, 'budget_management.html')

def graph_view(request):
    return render(request, 'graph.html')

def export_pdf(request):
    return render(request, 'export_pdf.html')

def export_csv(request):
    return render(request, 'export_csv.html')

def profile_view(request):
    return render(request, 'profile.html')