from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Category, PaymentMethod, Income, Expense
from itertools import chain
from operator import attrgetter
from .services import (authenticate_user, register_user, update_profile, change_password, get_income_sources, add_income_source,
                        delete_income_source, add_income, get_payment_methods, add_payment_method, delete_payment_method,
                        get_categories, add_category, delete_category, get_income_sources, get_categories, get_payment_methods,
                        add_expense, export_transactions_to_csv)

def base_view(request):
    user = User.objects.get(u_id=request.session['user_id'])  # Fetch user based on session
    return render(request, 'base.html', {'user': user})

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
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if user is not authenticated

    user = User.objects.get(u_id=request.session['user_id'])
    sources = get_income_sources(user)  # Fetch user's income sources
    methods = get_payment_methods(user) # Fetch user's payment methods

    if request.method == "POST":
        amount = request.POST.get('amount')
        source_id = request.POST.get('source_of_income')
        payment_method = request.POST.get('payment_method')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')

        success, message = add_income(user, source_id, amount, payment_method, description, date, time)
        messages.success(request, message) if success else messages.error(request, message)

        return redirect('index')  # Redirect after handling form submission

    return render(request, 'index.html', {'sources': sources, 'methods': methods})

def profile_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = User.objects.get(u_id=user_id)

    if request.method == "POST":
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        profile_picture = request.FILES.get('profile_picture')

        success, message = update_profile(user_id, first_name, last_name, profile_picture)
        messages.success(request, message) if success else messages.error(request, message)
        return redirect('profile')

    return render(request, 'profile.html', {'user': user})

def change_password_view(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']

    if request.method == "POST":
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
        else:
            success, message = change_password(user_id, current_password, new_password)
            messages.success(request, message) if success else messages.error(request, message)

        return redirect('change_password')

    return render(request, 'change_password.html')

def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('login')

def transactions_view(request):
    query = request.GET.get('q', '').strip()
    user = request.user

    # Fetch transactions for the user
    incomes = Income.objects.filter(user=user)
    expenses = Expense.objects.filter(user=user)

    # Apply search filter if query exists
    if query:
        incomes = incomes.filter(
            source__name__icontains=query
        ) | incomes.filter(
            payment_method__icontains=query
        ) | incomes.filter(
            date__icontains=query
        ) | incomes.filter(
            description__icontains=query
        )

        expenses = expenses.filter(
            category__name__icontains=query
        ) | expenses.filter(
            payment_method__name__icontains=query
        ) | expenses.filter(
            date__icontains=query
        ) | expenses.filter(
            description__icontains=query
        )

    # Merge and sort transactions
    transactions = sorted(
        chain(incomes, expenses),
        key=attrgetter('date', 'time'),
        reverse=True
    )

    # Convert expenses to negative values (optional, only if needed)
    for transaction in transactions:
        if isinstance(transaction, Expense):
            transaction.amount = -transaction.amount  # Make expense negative

    # Calculate Summary
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    total_balance = total_income + total_expense

    return render(request, 'transactions.html', {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_balance
    })

def expense_page(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if user is not authenticated

    user = User.objects.get(u_id=request.session['user_id'])
    
    # Fetch categories and payment methods for the user
    categories = get_categories(user)
    methods = get_payment_methods(user)

    return render(request, 'expense.html', {'categories': categories, 'methods': methods})

def add_expense_view(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if user is not authenticated

    user = User.objects.get(u_id=request.session['user_id'])
    categories = Category.objects.filter(user=user)  # Fetch user's categories
    methods = PaymentMethod.objects.filter(user=user)  # Fetch user's payment methods

    if request.method == "POST":
        amount = request.POST.get('amount')
        category_id = request.POST.get('category')
        payment_method_id = request.POST.get('payment_method')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')

        success, message = add_expense(user, category_id, amount, payment_method_id, description, date, time)
        messages.success(request, message) if success else messages.error(request, message)

        return redirect('add_expense')

    return render(request, 'expense.html', {'categories': categories, 'methods': methods})

def manage_categories_page(request):
    """Page to manage categories."""
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(u_id=request.session['user_id'])

    if request.method == "POST":
        category_name = request.POST.get('category_name')
        success, message = add_category(user, category_name)
        messages.success(request, message) if success else messages.error(request, message)
        return redirect('manage_categories')

    categories = get_categories(user)
    return render(request, "manage_categories.html", {'categories': categories})

def delete_category_view(request, category_id):
    """Delete a category."""
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(u_id=request.session['user_id'])
    success, message = delete_category(user, category_id)
    messages.success(request, message) if success else messages.error(request, message)
    return redirect('manage_categories')

def manage_payment_methods_page(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(u_id=request.session['user_id'])

    if request.method == "POST":
        method_name = request.POST.get('method_name')
        success, message = add_payment_method(user, method_name)
        messages.success(request, message) if success else messages.error(request, message)
        return redirect('manage_payment_methods')

    methods = get_payment_methods(user)
    return render(request, "manage_payment_methods.html", {"methods": methods})

def delete_payment_method_view(request, method_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(u_id=request.session['user_id'])
    success, message = delete_payment_method(user, method_id)
    messages.success(request, message) if success else messages.error(request, message)
    return redirect('manage_payment_methods')

def manage_source_of_income(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(u_id=request.session['user_id'])

    if request.method == "POST":
        source_name = request.POST.get('source_name')
        success, message = add_income_source(user, source_name)
        messages.success(request, message) if success else messages.error(request, message)
        return redirect('manage_source_of_income')

    sources = get_income_sources(user)
    return render(request, 'manage_source_of_income.html', {'sources': sources})

def delete_source_of_income(request, source_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user = User.objects.get(u_id=request.session['user_id'])
    success, message = delete_income_source(user, source_id)
    messages.success(request, message) if success else messages.error(request, message)
    return redirect('manage_source_of_income')

def budget_management(request):
    return render(request, 'budget_management.html')

def graph_view(request):
    return render(request, 'graph.html')

def export_pdf(request):
    return render(request, 'export_pdf.html')

def export_csv(request):
    """Renders the export page with the download button."""
    return render(request, 'export_csv.html')

def download_csv(request):
    """Handles the CSV download request."""
    if 'user_id' not in request.session:  # Ensure session-based authentication
        return redirect('login')  # Redirect if user is not authenticated

    return export_transactions_to_csv(request.session['user_id'])  # Pass session user ID