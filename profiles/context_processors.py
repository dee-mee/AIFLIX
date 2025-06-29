from .models import Profile

def profile_context(request):
    """Add profile-related context to all templates."""
    context = {
        'current_profile': None,
        'is_kids_profile': False,
        'allowed_maturity_levels': ['all', '7+', '13+', '16+', '18+'],  # Default to all
    }
    
    if hasattr(request, 'user') and request.user.is_authenticated:
        profile_id = request.session.get('profile_id')
        if profile_id:
            try:
                profile = Profile.objects.get(id=profile_id, user=request.user)
                context.update({
                    'current_profile': profile,
                    'is_kids_profile': profile.is_kids_profile(),
                    'allowed_maturity_levels': profile.get_allowed_maturity_levels(),
                })
            except Profile.DoesNotExist:
                # Clear invalid profile from session
                for key in ['profile_id', 'profile_name', 'profile_avatar']:
                    if key in request.session:
                        del request.session[key]
    
    return context
