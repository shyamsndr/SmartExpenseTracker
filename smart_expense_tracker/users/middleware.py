from django.shortcuts import redirect
from .models import User

class UserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Attach user to the context for every request if the user is logged in
        if 'user_id' in request.session:
            try:
                user = User.objects.get(u_id=request.session['user_id'])
                request.user = user
            except User.DoesNotExist:
                request.user = None
        else:
            request.user = None

        response = self.get_response(request)
        return response
