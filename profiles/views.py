from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import models
from .models import Profile, WatchHistory, MyList
from .forms import ProfileForm, ProfileSelectionForm
from movies.models import Movie
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

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
    """
    Display a list of profiles for the current user.
    If the user has only one profile and not coming from manage, automatically select it.
    """
    # Check if we're coming from the manage profiles page
    from_manage = request.GET.get('from_manage') == '1' or request.session.get('from_manage', False)
    
    # Clear the from_manage flag from session if it exists
    if 'from_manage' in request.session:
        del request.session['from_manage']
    
    # Get all profiles for the current user, ordered by name
    profiles = Profile.objects.filter(user=request.user).order_by('name')
    
    # Check if user has any profiles
    if not profiles.exists():
        return redirect('profiles:create')
    
    # Get the current profile ID from session if it exists
    current_profile_id = request.session.get('profile_id')
    
    # If we have a current profile in session, move it to the front of the list
    if current_profile_id:
        profiles = list(profiles)  # Convert to list for reordering
        try:
            # Find the current profile in the list
            current_profile = next(p for p in profiles if str(p.id) == current_profile_id)
            # Remove it from its current position and add to the front
            profiles.remove(current_profile)
            profiles.insert(0, current_profile)
        except (StopIteration, ValueError):
            # If the profile wasn't found, keep the original order
            pass
    
    # If user has only one profile and not coming from manage, auto-select it
    if len(profiles) == 1 and 'profile_id' not in request.session and not from_manage:
        profile = profiles[0]
        
        # Set the profile in the session
        request.session['profile_id'] = str(profile.id)
        request.session['profile_name'] = profile.name
        if profile.avatar:
            request.session['profile_avatar'] = profile.avatar.url
        
        # Set as default profile if not already set
        if not request.user.default_profile:
            request.user.default_profile = profile
            request.user.save()
        
        # Get the next URL from the request or session
        next_url = request.GET.get('next') or request.session.pop('next', None)
        
        # If no specific next URL, go to home
        if not next_url:
            return redirect('movies:home')
            
        # Handle relative URLs
        if next_url.startswith('/'):
            from urllib.parse import urlparse, parse_qs, urlencode
            parsed = urlparse(next_url)
            path = parsed.path
            
            # Clean up query parameters
            query = parse_qs(parsed.query)
            if 'from_manage' in query:
                del query['from_manage']
            
            # Rebuild the URL with cleaned query parameters
            if query:
                path = f"{path}?{urlencode(query, doseq=True)}"
            
            return redirect(path)
            
        return redirect(next_url)
    
    # If coming from manage profiles, set the flag in the session
    if from_manage:
        request.session['from_manage'] = True
    
    # Check if we need to show a message about profile selection
    show_selection_message = 'profile_id' not in request.session and not from_manage
    
    # Check for existing valid profile in session
    if 'profile_id' in request.session:
        try:
            profile = Profile.objects.get(id=request.session['profile_id'], user=request.user)
            
            # Update avatar in session if available
            if profile.avatar:
                request.session['profile_avatar'] = profile.avatar.url
            elif 'profile_avatar' in request.session:
                del request.session['profile_avatar']
            
            # If not coming from manage, redirect to home or next URL
            if not from_manage:
                next_url = request.GET.get('next') or 'movies:home'
                return redirect(next_url)
                
        except Profile.DoesNotExist:
            # Clear invalid profile data
            for key in ['profile_id', 'profile_name', 'profile_avatar']:
                if key in request.session:
                    del request.session[key]
            messages.warning(request, 'Your selected profile no longer exists. Please select a profile below.')
    
    context = {
        'profiles': profiles,
        'from_manage': from_manage,
        'show_selection_message': show_selection_message,
    }
    
    return render(request, 'profiles/profile_list.html', context)

@login_required
def select_profile(request, profile_id):
    """
    Select a profile to use for the current session.
    Handles profile selection, session management, and redirection.
    """
    import logging
    from urllib.parse import urlparse, parse_qs, urlencode
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get the profile and ensure it belongs to the current user
        profile = get_object_or_404(Profile, id=profile_id, user=request.user)
        
        # Debug logging
        logger.info(f"Selecting profile: {profile.name} (ID: {profile.id}) for user: {request.user.username}")
        
        # Get the from_manage flag from request or session
        from_manage = request.GET.get('from_manage') == '1' or request.session.get('from_manage', False)
        
        # Clear any existing profile data from session
        for key in ['profile_id', 'profile_name', 'profile_avatar']:
            if key in request.session:
                del request.session[key]
        
        # Set the new profile in the session
        request.session['profile_id'] = str(profile.id)  # Store as string for consistency
        request.session['profile_name'] = profile.name
        
        # Update avatar in session if available
        if profile.avatar:
            request.session['profile_avatar'] = profile.avatar.url
        
        # Set as default profile if not already set
        if not request.user.default_profile:
            request.user.default_profile = profile
            request.user.save()
        
        # Save the session explicitly
        request.session.modified = True
        
        # Get the next URL from the request or session
        next_url = request.GET.get('next') or request.session.pop('next', None)
        
        # If coming from manage profiles, go back to manage
        if from_manage:
            return redirect('profiles:manage')
        
        # If no specific next URL, go to home
        if not next_url:
            return redirect('movies:home')
        
        # Handle relative URLs
        if next_url.startswith('/'):
            # Parse the URL to get path and query parameters
            parsed = urlparse(next_url)
            path = parsed.path
            
            # Parse and clean up query parameters
            query = parse_qs(parsed.query)
            if 'from_manage' in query:
                del query['from_manage']
            
            # Rebuild the URL with cleaned query parameters
            if query:
                path = f"{path}?{urlencode(query, doseq=True)}"
            
            return redirect(path)
        
        # Handle named URLs
        return redirect(next_url)
        
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
    
    # Get the watchlist with related content to reduce database queries
    my_list_items = MyList.objects.filter(profile=profile).select_related('movie', 'series')
    
    # Group by content type (movie or series)
    movies = []
    series = []
    
    for item in my_list_items:
        if item.content_type == 'series':
            series.append(item.series if item.series else item.movie)
        else:
            movies.append(item.movie if item.movie else item.series)
    
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
    """Add or remove a movie or series from the user's watchlist."""
    if 'profile_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'No profile selected'}, status=400)
    
    profile = get_object_or_404(Profile, id=request.session['profile_id'], user=request.user)
    content = get_object_or_404(Movie, id=movie_id)
    
    # Check if the content is already in the user's list
    my_list_item = MyList.objects.filter(
        profile=profile,
        **{'series' if content.is_series else 'movie': content}
    ).first()
    
    if my_list_item:
        my_list_item.delete()
        return JsonResponse({'status': 'removed', 'message': 'Removed from My List'})
    else:
        # Create new entry
        if content.is_series:
            MyList.objects.create(profile=profile, series=content)
        else:
            MyList.objects.create(profile=profile, movie=content)
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

@login_required
@require_http_methods(["POST"])
@csrf_exempt  # For demo purposes only - in production, use proper CSRF handling
@require_POST
def update_watch_history(request, movie_id):
    """Update watch history for the current profile and movie."""
    if 'profile_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'No profile selected'}, status=400)
    
    try:
        profile = Profile.objects.get(id=request.session['profile_id'], user=request.user)
        movie = Movie.objects.get(id=movie_id)
        
        # Get progress from request body (form data or JSON)
        progress = float(request.POST.get('progress', 0))
        
        # Update or create watch history
        watch_history, created = WatchHistory.objects.update_or_create(
            profile=profile,
            movie=movie,
            defaults={'progress': progress}
        )
        
        return JsonResponse({
            'status': 'success', 
            'progress': watch_history.progress,
            'created': created
        })
        
    except (Profile.DoesNotExist, Movie.DoesNotExist, ValueError) as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)