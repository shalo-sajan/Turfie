from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def player_required(view_func):
    """
    Decorator for views that checks that the user is a player.
    Redirects to the appropriate dashboard if the test fails.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_turf_owner and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You are not authorized to view this page.")
            # Redirect to the user's actual dashboard or login
            if request.user.is_authenticated:
                return redirect(request.user.get_dashboard_url())
            return redirect('users:login')
    return wrapper


def turf_owner_required(view_func):
    """
    Decorator for views that checks that the user is a turf owner.
    Redirects to the appropriate dashboard if the test fails.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_turf_owner and not request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You are not authorized to view this page.")
            # Redirect to the user's actual dashboard or login
            if request.user.is_authenticated:
                return redirect(request.user.get_dashboard_url())
            return redirect('users:login')
    return wrapper

