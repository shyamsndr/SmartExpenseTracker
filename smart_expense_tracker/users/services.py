from .models import User
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

def update_profile(user_id, first_name, last_name, profile_picture):
    """Update user profile details without losing existing data."""
    try:
        user = User.objects.get(u_id=user_id)

        # Update only if values are provided
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_picture:
            user.profile_picture = profile_picture  # Ensure file is stored correctly

        user.save()
        return True, "Profile updated successfully!"
    except User.DoesNotExist:
        return False, "User not found."


def change_password(user_id, current_password, new_password):
    """Change user password after verifying the old one."""
    try:
        user = User.objects.get(u_id=user_id)
        if not check_password(current_password, user.password):
            return False, "Current password is incorrect."
        
        user.password = make_password(new_password)
        user.save()
        return True, "Password changed successfully!"
    except User.DoesNotExist:
        return False, "User not found."