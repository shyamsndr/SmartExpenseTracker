from .models import User, SourceOfIncome, Income, PaymentMethod, Category, Expense
from django.contrib.auth.hashers import make_password, check_password
import csv
from django.http import HttpResponse

def authenticate_user(email, password):
    """Authenticate user by checking email and password."""
    try:
        user = User.objects.get(email=email)
        if check_password(password, user.password):
            return user
    except User.DoesNotExist:
        return None
    return None

def register_user(email, password, confirm_password):
    """Register a new user after validation."""
    if password != confirm_password:
        return False, "Passwords do not match."

    if User.objects.filter(email=email).exists():
        return False, "Email is already registered."

    hashed_password = make_password(password)
    User.objects.create(email=email, password=hashed_password)

    return True, "Registration successful!"

def update_profile(user_id, first_name=None, last_name=None, profile_picture=None):
    """Update user profile details without losing existing data."""
    try:
        user = User.objects.get(u_id=user_id)

        # Update only if values are provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_picture:
            user.profile_picture = profile_picture  # Ensures the file is stored correctly

        user.save()
        return True, "Profile updated successfully!"
    except User.DoesNotExist:
        return False, "User not found."

def change_password(user_id, current_password, new_password):
    """Change user password after verifying the old one."""
    try:
        user = User.objects.get(u_id=user_id)
        
        # Verify old password
        if not check_password(current_password, user.password):
            return False, "Current password is incorrect."
        
        # Prevent setting the same password again
        if check_password(new_password, user.password):
            return False, "New password cannot be the same as the current password."
        
        # Hash and save new password
        user.password = make_password(new_password)
        user.save()
        return True, "Password changed successfully!"
    except User.DoesNotExist:
        return False, "User not found."
    
def get_income_sources(user):
    return SourceOfIncome.objects.filter(user=user)

def add_income_source(user, name):
    """Add a new income source if it doesn't already exist."""
    if SourceOfIncome.objects.filter(user=user, name=name).exists():
        return False, "Source already exists."

    SourceOfIncome.objects.create(user=user, name=name)
    return True, "Source added successfully."

def delete_income_source(user, source_id):
    """Delete an income source if the user owns it."""
    try:
        source = SourceOfIncome.objects.get(user=user, source_id=source_id)
        source.delete()
        return True, "Source deleted successfully."
    except SourceOfIncome.DoesNotExist:
        return False, "Source not found."
    
def add_income(user, source_id, amount, payment_method_id, description, date, time):
    """Handles adding a new income transaction."""
    try:
        source = SourceOfIncome.objects.get(user=user, source_id=source_id)
        payment_method = PaymentMethod.objects.get(user=user, method_id = payment_method_id)

        # Save income entry
        Income.objects.create(
            user=user,
            source=source,
            amount=amount,
            payment_method=payment_method,
            description=description,
            date=date,
            time=time
        )
        return True, "Income added successfully!"
    except (SourceOfIncome.DoesNotExist, PaymentMethod.DoesNotExist):
        return False, "Invalid source of income."
    except Exception as e:
        return False, str(e)
    
#manage payment methods
def get_payment_methods(user):
    """Fetch all payment methods for a user."""
    return PaymentMethod.objects.filter(user=user)

def add_payment_method(user, name):
    """Add a new payment method if it doesn't already exist."""
    if PaymentMethod.objects.filter(user=user, name=name).exists():
        return False, "Payment method already exists."

    PaymentMethod.objects.create(user=user, name=name)
    return True, "Payment method added successfully."

def delete_payment_method(user, method_id):
    """Delete a payment method if the user owns it."""
    try:
        method = PaymentMethod.objects.get(user=user, method_id=method_id)
        method.delete()
        return True, "Payment method deleted successfully."
    except PaymentMethod.DoesNotExist:
        return False, "Payment method not found."
    
#manage categories
def get_categories(user):
    """Fetch all categories for a user."""
    return Category.objects.filter(user=user)

def add_category(user, name):
    """Add a new category if it doesn't already exist."""
    if Category.objects.filter(user=user, name=name).exists():
        return False, "Category already exists."
    
    Category.objects.create(user=user, name=name)
    return True, "Category added successfully."

def delete_category(user, category_id):
    """Delete a category if the user owns it."""
    try:
        category = Category.objects.get(user=user, category_id=category_id)
        category.delete()
        return True, "Category deleted successfully."
    except Category.DoesNotExist:
        return False, "Category not found."
    
#inserting expenses    
def add_expense(user, category_id, amount, payment_method_id, description, date, time):
    """Handles adding a new expense transaction."""
    try:
        category = Category.objects.get(user=user, category_id=category_id)
        payment_method = PaymentMethod.objects.get(user=user, method_id=payment_method_id)

        # Save expense entry
        Expense.objects.create(
            user=user,
            category=category,
            payment_method=payment_method,
            amount=amount,
            description=description,
            date=date,
            time=time
        )
        return True, "Expense added successfully!"
    except (Category.DoesNotExist, PaymentMethod.DoesNotExist):
        return False, "Invalid category or payment method."
    except Exception as e:
        return False, str(e)
    
def export_transactions_to_csv(user):
    """Generate and return a CSV file with both income and expenses."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Type', 'Description', 'Amount', 'Category'])

    # Fetch both expenses and incomes
    expenses = Expense.objects.filter(user=user)
    incomes = Income.objects.filter(user=user)

    # Write expense data
    for expense in expenses:
        writer.writerow([
            expense.date.strftime('%Y-%m-%d'),
            'Expense',
            expense.description,
            expense.amount,
            expense.category
        ])

    # Write income data
    for income in incomes:
        writer.writerow([
            income.date.strftime('%Y-%m-%d'),
            'Income',
            income.description,
            income.amount,
            income.source  # Assuming 'source' is the category for income
        ])

    return response