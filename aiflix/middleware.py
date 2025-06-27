from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page except
    those specified in PUBLIC_URLS.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Public URLs that don't require authentication
        self.public_urls = [
            reverse('landing'),
            reverse('accounts:login'),
            reverse('accounts:register'),
            reverse('accounts:password_reset'),
            reverse('accounts:password_reset_done'),
            reverse('profiles:profile_list'),
            '/profiles/select/',  # Allow access to profile selection
            '/static/',
            '/media/',
        ]
        if settings.DEBUG:
            self.public_urls.extend([
                '/__debug__/',
                '/admin/',
            ])

    def __call__(self, request):
        # Skip middleware for static and media files
        if any(request.path.startswith(url) for url in ['/static/', '/media/']):
            return self.get_response(request)
            
        # Allow access to public URLs
        if any(request.path.startswith(url) for url in self.public_urls):
            return self.get_response(request)
            
        # Allow authenticated users
        if request.user.is_authenticated:
            return self.get_response(request)
            
        # Redirect unauthenticated users to login page
        login_url = reverse('accounts:login') + f'?next={request.path}'
        return redirect(login_url)
