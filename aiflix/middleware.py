import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

logger = logging.getLogger(__name__)

class LoginRequiredMiddleware:
    """
    Middleware that requires a user to be authenticated to view any page except
    those specified in PUBLIC_URLS.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Public URLs that don't require authentication
        self.public_urls = [
            '/',  # Landing page
            '/accounts/login/',
            '/accounts/register/',
            '/accounts/password_reset/',
            '/accounts/password_reset/done/',
            '/profiles/profile_list/',
            '/profiles/select/',  # Allow access to profile selection
            '/static/',
            '/media/',
            '/favicon.ico',  # Add favicon explicitly
        ]
        if settings.DEBUG:
            self.public_urls.extend([
                '/__debug__/',
                '/admin/',
            ])
        logger.info(f"Initialized LoginRequiredMiddleware with public URLs: {self.public_urls}")

    def __call__(self, request):
        logger.info(f"Processing request: {request.path}")
        
        # Skip middleware for static and media files
        if any(request.path.startswith(url) for url in ['/static/', '/media/']):
            logger.info(f"Allowing static/media file: {request.path}")
            return self.get_response(request)
            
        # Allow access to public URLs
        if any(request.path == url or request.path.startswith(url) for url in self.public_urls):
            logger.info(f"Allowing public URL: {request.path}")
            return self.get_response(request)
            
        # Allow authenticated users
        if request.user.is_authenticated:
            logger.info(f"Allowing authenticated user: {request.path}")
            return self.get_response(request)
            
        # Redirect unauthenticated users to login page
        logger.info(f"Redirecting unauthenticated user from: {request.path}")
        login_url = reverse('accounts:login') + f'?next={request.path}'
        return redirect(login_url)
