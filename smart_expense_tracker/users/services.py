from .models import User, SourceOfIncome
from django.contrib.auth.hashers import make_password, check_password

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
    """Retrieve all income sources for the user."""
    return SourceOfIncome.objects.filter(user=user).order_by('name')

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