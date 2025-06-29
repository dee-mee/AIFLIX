from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile

class ProfileMiddleware:
    """
    Middleware to ensure users have a valid profile selected.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.


    def __call__(self, request):
        # Skip for static files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
            
        # Skip for auth and profile management URLs
        auth_urls = [
            '/accounts/login/',
            '/accounts/register/',
            '/accounts/logout/',
            '/profiles/',
            '/profiles/select/',
            '/profiles/create/',
            '/profiles/manage/',
        ]
        
        if any(request.path.startswith(url) for url in auth_urls):
            return self.get_response(request)
            
        # For authenticated users
        if hasattr(request, 'user') and request.user.is_authenticated:
            # If no profile is selected but user has profiles, redirect to profile selection
            if 'profile_id' not in request.session and request.user.profiles.exists():
                return redirect('profiles:profile_list')
                
            # If a profile is selected, verify it exists and belongs to the user
            if 'profile_id' in request.session:
                try:
                    profile = Profile.objects.get(
                        id=request.session['profile_id'],
                        user=request.user
                    )
                    # Update session data if needed
                    if 'profile_name' not in request.session or \
                       request.session['profile_name'] != profile.name:
                        request.session['profile_name'] = profile.name
                        
                    if profile.avatar:
                        request.session['profile_avatar'] = profile.avatar.url
                    elif 'profile_avatar' in request.session:
                        del request.session['profile_avatar']
                        
                except Profile.DoesNotExist:
                    # Clear invalid profile data
                    for key in ['profile_id', 'profile_name', 'profile_avatar']:
                        if key in request.session:
                            del request.session[key]
                    return redirect('profiles:profile_list')
        
        response = self.get_response(request)
        return response
