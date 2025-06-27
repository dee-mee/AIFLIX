from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Profile, WatchHistory, MyList
from .forms import ProfileForm, ProfileSelectionForm
from movies.models import Movie
from django.views.generic import CreateView
from django.urls import reverse_lazy

class CreateProfileView(CreateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_form.html'
    success_url = reverse_lazy('profiles:profile_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Profile created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Profile'
        return context

@login_required
def profile_list(request):
    """List all profiles for the current user."""
    profiles = request.user.profiles.all()
    
    # If user has no profiles, show a message
    if not profiles.exists():
        messages.info(request, 'No profiles found. Please contact support for assistance.')
    
    # If user has only one profile and it's not selected, select it automatically
    if len(profiles) == 1 and 'profile_id' not in request.session:
        profile = profiles[0]
        request.session['profile_id'] = str(profile.id)
        request.session['profile_name'] = profile.name
        if profile.avatar:
            request.session['profile_avatar'] = profile.avatar.url
        return redirect('movies:home')
    
    # Allow users to access the profile list at any time
    # Only redirect if they have no profiles at all
    if not profiles.exists() and 'profile_id' in request.session:
        # Clear all profile-related session data
        for key in ['profile_id', 'profile_name', 'profile_avatar']:
            if key in request.session:
                del request.session[key]
        messages.warning(request, 'Your selected profile no longer exists. Please create a new one.')
    
    # Ensure the selected profile still exists
    if 'profile_id' in request.session:
        try:
            profile = profiles.get(id=request.session['profile_id'])
            # Update session data if needed
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
    
    return render(request, 'profiles/profile_list.html', {
        'profiles': profiles,
    })

@login_required
def select_profile(request, profile_id):
    """
    Select a profile to use for the current session.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get the profile and ensure it belongs to the current user
        profile = get_object_or_404(Profile, id=profile_id, user=request.user)
        
        # Debug logging
        logger.info(f"Selecting profile: {profile.name} (ID: {profile.id}) for user: {request.user.username}")
        
        # Clear any existing profile data
        if 'profile_id' in request.session:
            del request.session['profile_id']
        if 'profile_name' in request.session:
            del request.session['profile_name']
            
        # Set the new profile in the session
        request.session['profile_id'] = str(profile.id)  # Ensure it's a string for consistency
        request.session['profile_name'] = profile.name
        if profile.avatar:
            request.session['profile_avatar'] = profile.avatar.url
        else:
            request.session.pop('profile_avatar', None)
        
        # Set session expiry to 30 days
        request.session.set_expiry(60 * 60 * 24 * 30)
        
        # Save the session explicitly
        request.session.save()
        
        # Debug logging
        logger.info(f"Session after setting profile: {dict(request.session)}")
        
        # Get the next URL, default to movies:home
        next_url = request.GET.get('next', 'movies:home')
        
        # Basic security check to prevent open redirects
        if not (next_url.startswith('/') or next_url.startswith('http')):
            next_url = 'movies:home'
        
        # If it's not a safe URL, default to home
        from urllib.parse import urlparse
        try:
            result = urlparse(next_url)
            if result.scheme or result.netloc:
                next_url = 'movies:home'
        except:
            next_url = 'movies:home'
        
        logger.info(f"Redirecting to: {next_url}")
        
        # Force a hard redirect to ensure the session is saved
        response = redirect(next_url)
        return response
        
    except Exception as e:
        logger.error(f"Error selecting profile: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while selecting the profile. Please try again.")
        return redirect('profiles:profile_list')

@login_required
def my_list(request):
    """View the user's watchlist."""
    # Check if a profile is selected
    if 'profile_id' not in request.session:
        messages.warning(request, 'Please select a profile to view your watchlist.')
        return redirect('profiles:profile_list')
    
    # Get the current profile
    try:
        profile = Profile.objects.get(id=request.session['profile_id'], user=request.user)
    except Profile.DoesNotExist:
        # Handle case where profile was deleted but session still has the ID
        del request.session['profile_id']
        messages.warning(request, 'Please select a profile to continue.')
        return redirect('profiles:profile_list')
    
    # Get the watchlist with related movies to reduce database queries
    my_list_items = MyList.objects.filter(profile=profile).select_related('movie')
    
    # Group by content type (movie or series)
    movies = []
    series = []
    
    for item in my_list_items:
        if item.movie.is_series:
            series.append(item.movie)
        else:
            movies.append(item.movie)
    
    # Check if the request is an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'movies': [{
                'id': m.id,
                'title': m.title,
                'thumbnail_url': m.thumbnail.url if m.thumbnail else '',
                'url': m.get_absolute_url(),
            } for m in movies],
            'series': [{
                'id': s.id,
                'title': s.title,
                'thumbnail_url': s.thumbnail.url if s.thumbnail else '',
                'url': s.get_absolute_url(),
            } for s in series],
        })
    
    return render(request, 'profiles/my_list.html', {
        'profile': profile,
        'movies': movies,
        'series': series,
        'total_items': len(movies) + len(series),
    })

@login_required
@require_POST
def toggle_my_list(request, movie_id):
    """Add or remove a movie from the user's watchlist."""
    if 'profile_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'No profile selected'}, status=400)
    
    profile = get_object_or_404(Profile, id=request.session['profile_id'], user=request.user)
    movie = get_object_or_404(Movie, id=movie_id)
    
    my_list_item, created = MyList.objects.get_or_create(
        profile=profile,
        movie=movie,
        defaults={'profile': profile, 'movie': movie}
    )
    
    if not created:
        my_list_item.delete()
        return JsonResponse({'status': 'removed', 'message': 'Removed from My List'})
    
    return JsonResponse({'status': 'added', 'message': 'Added to My List'})

@login_required
def delete_profile(request, profile_id):
    """Delete a user's profile."""
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    
    # Don't allow deleting the last profile
    if request.user.profiles.count() <= 1:
        messages.error(request, 'You cannot delete your only profile.')
        return redirect('profiles:profile_list')
    
    # If the profile being deleted is the currently selected one, update the session
    if 'profile_id' in request.session and int(request.session['profile_id']) == profile.id:
        # Select another profile
        new_profile = request.user.profiles.exclude(id=profile.id).first()
        if new_profile:
            request.session['profile_id'] = new_profile.id
        else:
            del request.session['profile_id']
    
    # Delete the profile
    profile_name = profile.name
    profile.delete()
    
    messages.success(request, f'Profile "{profile_name}" has been deleted.')
    return redirect('profiles:profile_list')
