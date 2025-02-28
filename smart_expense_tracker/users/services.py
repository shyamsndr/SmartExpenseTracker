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