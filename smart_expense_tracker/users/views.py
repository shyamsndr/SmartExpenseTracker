from django.shortcuts import render, redirect
from django.contrib import messages
from .services import authenticate_user, register_user

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate_user(email, password)
        if user:
            request.session['user_id'] = user.u_id  # Store user ID in session
            messages.success(request, "Logged in successfully!")
            return redirect('index')
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'pages-sign-in.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        success, message = register_user(email, password, confirm_password)
        if success:
            messages.success(request, message)
            return redirect('login')
        else:
            messages.error(request, message)

    return render(request, 'pages-sign-up.html')


def index(request):
    # Check if user is logged in
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if not authenticated
    return render(request, 'index.html')


def logout_view(request):
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