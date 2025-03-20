from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Category, PaymentMethod, Income, Expense, Budget
from django.db.models import Sum
from decimal import Decimal
import calendar
from datetime import datetime
from django.db.models import Q
from django.db import models
import plotly.express as px
import plotly.graph_objs as go
from plotly.offline import plot
from django.contrib import messages
from itertools import chain
from operator import attrgetter
from .services import (authenticate_user, register_user, update_profile, change_password, get_income_sources, add_income_source,
                        delete_income_source, add_income, get_payment_methods, add_payment_method, delete_payment_method,
                        get_categories, add_category, delete_category, get_income_sources, get_categories, get_payment_methods,
                        add_expense, export_transactions_to_csv, generate_transactions_pdf)

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
            Q(source__name__icontains=query) |
            Q(payment_method__name__icontains=query) |  # Fixed ForeignKey lookup
            Q(date__icontains=query) |
            Q(description__icontains=query)
        )

        expenses = expenses.filter(
            Q(category__name__icontains=query) |
            Q(payment_method__name__icontains=query) |  # Fixed ForeignKey lookup
            Q(date__icontains=query) |
            Q(description__icontains=query)
        )

    # Merge and sort transactions
    transactions = sorted(
        chain(incomes, expenses),
        key=attrgetter('date', 'time'),
        reverse=True
    )

    # Assign a common transaction_id for both Income and Expense
    for transaction in transactions:
        transaction.transaction_id = (
            transaction.income_id if isinstance(transaction, Income) else transaction.expense_id
        )

    # Convert expenses to negative values (optional)
    for transaction in transactions:
        if isinstance(transaction, Expense):
            transaction.amount = -transaction.amount

    # Calculate Summary
    total_income = sum(income.amount for income in incomes)
    total_expense = sum(expense.amount for expense in expenses)
    total_balance = total_income + total_expense  # Fixed: expenses are negative

    return render(request, 'transactions.html', {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_balance': total_balance
    })

def edit_transaction(request, transaction_id):
    # Try to fetch the transaction using the provided transaction_id
    try:
        transaction = Income.objects.get(income_id=transaction_id, user=request.user)
    except Income.DoesNotExist:
        transaction = Expense.objects.get(expense_id=transaction_id, user=request.user)

    if request.method == 'POST':
        # Update the transaction with the form data
        transaction.description = request.POST.get('description', transaction.description)
        transaction.amount = float(request.POST.get('amount', transaction.amount))
        transaction.save()
        return redirect('transactions')

    return render(request, 'edit_transaction.html', {'transaction': transaction})

def delete_transaction(request, transaction_id):
    # Try to fetch the transaction using the provided transaction_id
    try:
        transaction = Income.objects.get(income_id=transaction_id, user=request.user)
    except Income.DoesNotExist:
        transaction = Expense.objects.get(expense_id=transaction_id, user=request.user)

    if request.method == 'POST':
        # Delete the transaction
        transaction.delete()
        return redirect('transactions')

    return render(request, 'delete_transaction.html', {'transaction': transaction})

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
        messages.error(request, "You must be logged in!")
        return redirect('login')

    user = User.objects.get(u_id=request.session['user_id'])
    categories = Category.objects.filter(user=user)  
    methods = PaymentMethod.objects.filter(user=user)  

    if request.method == "POST":
        amount = Decimal(request.POST.get('amount'))
        category_id = request.POST.get('category')
        payment_method_id = request.POST.get('payment_method')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')

        category = Category.objects.get(user=user, category_id=category_id)

        # **Get month and year of the expense**
        expense_date = datetime.strptime(date, "%Y-%m-%d")
        expense_month, expense_year = expense_date.month, expense_date.year

        # **Filter budget for the expense's month**
        budget = Budget.objects.filter(user=user, category=category, month=expense_month, year=expense_year).first()

        # **Calculate total spent for this category in the same month**
        total_spent = Expense.objects.filter(
            user=user, category=category,
            date__year=expense_year, date__month=expense_month
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

        success, message = add_expense(user, category_id, amount, payment_method_id, description, date, time)

        # **Show Budget Warning But Allow Expense Entry**
        if budget and (total_spent + amount) > budget.limit:
            messages.warning(request, f"Warning: Budget exceeded for {category.name}! (Limit: ₹{budget.limit})")

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
    user_id = request.session.get('user_id')  # Get logged-in user ID from session
    if not user_id:
        messages.error(request, "You must be logged in!")
        return redirect('login')

    user = User.objects.get(u_id=user_id)

    if request.method == "POST":
        category_id = request.POST.get("category")
        limit = request.POST.get("limit")
        current_date = datetime.now()
        month, year = current_date.month, current_date.year  # Get current month and year

        if not category_id or not limit:
            messages.error(request, "Please enter all required fields.")
            return redirect("budget_management")

        category = Category.objects.get(category_id=category_id, user=user)
        
        # Create or update budget for the **current month**
        budget, created = Budget.objects.update_or_create(
            user=user, category=category, month=month, year=year,
            defaults={"limit": limit}
        )

        messages.success(request, f"Budget for {category.name} set to ₹{limit} for {month}/{year}")
        return redirect("budget_management")

    # Fetch budgets for the **current month only**
    current_date = datetime.now()
    categories = Category.objects.filter(user=user)
    budgets = Budget.objects.filter(user=user, month=current_date.month, year=current_date.year)

    return render(request, "budget_management.html", {"categories": categories, "budgets": budgets})

def delete_budget(request, budget_id):
    budget = Budget.objects.get(budget_id=budget_id)
    budget.delete()
    messages.success(request, "Budget removed successfully.")
    return redirect("budget_management")

def graph_view(request):
    try:
        # Fetch the current user from the session
        user_id = request.session.get('user_id')  # Assuming 'user_id' is stored in session
        
        if not user_id:
            messages.error(request, "No user found in session!")
            return render(request, 'graph.html')

        # Fetch the user object
        user = User.objects.get(u_id=user_id)

        # Get income and expense data for the current user
        income_data = Income.objects.filter(user=user)
        expense_data = Expense.objects.filter(user=user)

        # Summing income and expenses by category
        income_by_category = income_data.values('source__name').annotate(total_income=models.Sum('amount'))
        expense_by_category = expense_data.values('category__name').annotate(total_expense=models.Sum('amount'))

        # Prepare data for the donut chart
        income_labels = [item['source__name'] for item in income_by_category]
        expense_labels = [item['category__name'] for item in expense_by_category]

        # Combine income and expense labels and amounts
        labels = income_labels + expense_labels
        values = [item['total_income'] for item in income_by_category] + [item['total_expense'] for item in expense_by_category]

        # Create a Plotly Donut Chart
        trace = go.Pie(
            labels=labels,
            values=values,
            hole=0.4,  # Makes it a donut chart
            textinfo='percent+label',
            marker=dict(colors=['#008000', '#FF0000', '#00FF00', '#0000FF', '#FF00FF'])  # Customize colors
        )

        layout = go.Layout(
            title='Income vs Expense Analysis',
            showlegend=True
        )

        # Generate the graph's HTML
        graph_figure = go.Figure(data=[trace], layout=layout)
        graph_html = plot(graph_figure, output_type='div')

        # Render the template with the graph
        return render(request, 'graph.html', {'graph_html': graph_html})
    
    except Exception as e:
        messages.error(request, f"Error occurred: {str(e)}")
        return render(request, 'graph.html')

def export_pdf(request):
    """Renders the export page with the download button."""
    return render(request, 'export_pdf.html')

def download_pdf(request):
    """Handles the PDF download request."""
    if 'user_id' not in request.session:  # Ensure session-based authentication
        return redirect('login')  # Redirect if user is not authenticated

    return generate_transactions_pdf(request.session['user_id']) 

def export_csv(request):
    """Renders the export page with the download button."""
    return render(request, 'export_csv.html')

def download_csv(request):
    """Handles the CSV download request."""
    if 'user_id' not in request.session:  # Ensure session-based authentication
        return redirect('login')  # Redirect if user is not authenticated

    return export_transactions_to_csv(request.session['user_id'])  # Pass session user ID

def compare_months_view(request):
    user = request.user  # Get the logged-in user

    # Retrieve session data or set default values
    selected_year = request.session.get('selected_year', str(datetime.now().year))
    month1 = request.session.get('month1', '1')
    month2 = request.session.get('month2', '2')

    if request.method == "GET":
        selected_year = request.GET.get('year', selected_year)
        month1 = request.GET.get('month1', month1)
        month2 = request.GET.get('month2', month2)

        # Save selections in session
        request.session['selected_year'] = selected_year
        request.session['month1'] = month1
        request.session['month2'] = month2

    income_month1 = income_month2 = expense_month1 = expense_month2 = None
    balance_month1 = balance_month2 = 0
    month1_name = month2_name = ""

    if selected_year and month1 and month2:
        # Convert month numbers to names
        month1_name = calendar.month_name[int(month1)]
        month2_name = calendar.month_name[int(month2)]

        # Get total income and expense for each selected month
        income_month1 = Income.objects.filter(
            user=user, date__year=selected_year, date__month=month1
        ).aggregate(total_income=Sum('amount'))['total_income'] or 0

        income_month2 = Income.objects.filter(
            user=user, date__year=selected_year, date__month=month2
        ).aggregate(total_income=Sum('amount'))['total_income'] or 0

        expense_month1 = Expense.objects.filter(
            user=user, date__year=selected_year, date__month=month1
        ).aggregate(total_expense=Sum('amount'))['total_expense'] or 0

        expense_month2 = Expense.objects.filter(
            user=user, date__year=selected_year, date__month=month2
        ).aggregate(total_expense=Sum('amount'))['total_expense'] or 0

        # Calculate balance for each month
        balance_month1 = income_month1 - expense_month1
        balance_month2 = income_month2 - expense_month2

    # Generate year and month choices
    years = [str(y) for y in range(datetime.now().year, datetime.now().year - 5, -1)]
    months = [{"number": str(m), "name": calendar.month_name[m]} for m in range(1, 13)]

    context = {
        'selected_year': selected_year,
        'month1': month1,
        'month2': month2,
        'month1_name': month1_name,
        'month2_name': month2_name,
        'income_month1': income_month1,
        'income_month2': income_month2,
        'expense_month1': expense_month1,
        'expense_month2': expense_month2,
        'balance_month1': balance_month1,
        'balance_month2': balance_month2,
        'years': years,
        'months': months,
    }
    return render(request, 'compare_months.html', context)

def compare_years_view(request):
    user = request.user  # Get the logged-in user

    # Retrieve session data or set default values
    year1 = request.session.get('year1', str(datetime.now().year - 1))
    year2 = request.session.get('year2', str(datetime.now().year))

    if request.method == "GET":
        year1 = request.GET.get('year1', year1)
        year2 = request.GET.get('year2', year2)

        # Save selections in session
        request.session['year1'] = year1
        request.session['year2'] = year2

    income_year1 = income_year2 = expense_year1 = expense_year2 = None
    balance_year1 = balance_year2 = 0

    if year1 and year2:
        # Get total income and expense for each selected year
        income_year1 = Income.objects.filter(
            user=user, date__year=year1
        ).aggregate(total_income=Sum('amount'))['total_income'] or 0

        income_year2 = Income.objects.filter(
            user=user, date__year=year2
        ).aggregate(total_income=Sum('amount'))['total_income'] or 0

        expense_year1 = Expense.objects.filter(
            user=user, date__year=year1
        ).aggregate(total_expense=Sum('amount'))['total_expense'] or 0

        expense_year2 = Expense.objects.filter(
            user=user, date__year=year2
        ).aggregate(total_expense=Sum('amount'))['total_expense'] or 0

        # Calculate balance for each year
        balance_year1 = income_year1 - expense_year1
        balance_year2 = income_year2 - expense_year2

    # Generate year choices
    years = [str(y) for y in range(datetime.now().year, datetime.now().year - 5, -1)]

    context = {
        'year1': year1,
        'year2': year2,
        'income_year1': income_year1,
        'income_year2': income_year2,
        'expense_year1': expense_year1,
        'expense_year2': expense_year2,
        'balance_year1': balance_year1,
        'balance_year2': balance_year2,
        'years': years,
    }
    return render(request, 'compare_years.html', context)