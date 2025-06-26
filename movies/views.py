from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F, Case, When, Value, IntegerField
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.db.models.functions import Coalesce
from .models import Movie, Genre, Season, Episode, Rating
from profiles.models import WatchHistory, MyList

def get_base_queryset():
    """Base queryset for movies with common filters and annotations."""
    return Movie.objects.filter(
        is_active=True
    ).annotate(
        has_poster=Case(
            When(thumbnail__isnull=False, then=Value(1)),
            default=Value(0),
            output_field=IntegerField()
        )
    ).order_by('-has_poster', '-release_date')

def home(request):
    """Home page with featured and trending content."""
    # Get genre filter if any
    genre_slug = request.GET.get('genre')
    genre_filter = {}
    
    if genre_slug:
        try:
            genre = Genre.objects.get(slug=genre_slug)
            genre_filter = {'genres': genre}
        except Genre.DoesNotExist:
            raise Http404("Genre not found")
    
    # Base queryset with common filters
    base_queryset = get_base_queryset()
    
    # Apply genre filter if specified
    if genre_filter:
        base_queryset = base_queryset.filter(**genre_filter)
    
    # Featured content
    featured_movies = base_queryset.filter(
        is_featured=True
    ).order_by('-release_date')
    
    # If no genre filter, show trending movies
    if not genre_filter:
        trending_movies = base_queryset.filter(
            is_trending=True
        ).order_by('-trending_score', '-release_date')[:10]
    else:
        trending_movies = base_queryset.order_by('-trending_score', '-release_date')[:10]
    
    # Popular content (based on ratings, views, and recency)
    popular_movies = base_queryset.annotate(
        popularity_score=(
            F('views') * 0.4 + 
            F('average_rating') * 60 +  # Assuming 10-point scale
            F('created_at__year') * 0.1  # Slight boost for newer content
        )
    ).order_by('-popularity_score')[:10]
    
    # Recently added content
    recent_movies = base_queryset.order_by('-created_at')[:10]
    
    # Group by content type if no genre filter
    if not genre_filter:
        movies = base_queryset.filter(
            content_type='movie'
        ).order_by('-release_date')[:10]
        
        series = base_queryset.filter(
            content_type='series'
        ).order_by('-release_date')[:10]
        
        documentaries = base_queryset.filter(
            content_type='documentary'
        ).order_by('-release_date')[:10]
    else:
        # If genre filter is applied, don't show these sections
        movies = series = documentaries = Movie.objects.none()
    
    # Get all genres for navigation
    all_genres = Genre.objects.all().order_by('name')
    
    # Get popular genres (genres with most movies)
    popular_genres = Genre.objects.annotate(
        num_movies=Count('movie', filter=Q(movie__is_active=True))
    ).filter(
        num_movies__gt=0
    ).order_by('-num_movies')[:8]
    
    # Get watch history for the current profile
    watch_history = []
    if 'profile_id' in request.session and not genre_filter:
        try:
            watch_history = WatchHistory.objects.filter(
                profile_id=request.session['profile_id'],
                movie__isnull=False
            ).select_related('movie').order_by('-watched_at')[:10]
            
            # Filter out any None movies and ensure they're active
            watch_history = [
                item for item in watch_history 
                if hasattr(item, 'movie') and hasattr(item.movie, 'is_active') and item.movie.is_active
            ][:10]
        except (WatchHistory.DoesNotExist, KeyError, AttributeError):
            pass
    
    context = {
        'featured_movies': featured_movies,
        'trending_movies': trending_movies,
        'popular_movies': popular_movies,
        'recent_movies': recent_movies,
        'movies': movies,
        'series': series,
        'documentaries': documentaries,
        'watch_history': watch_history,
        'all_genres': all_genres,
        'popular_genres': popular_genres,
    }
    
    return render(request, 'movies/home.html', context)

def movie_detail(request, pk, slug=None):
    """Detailed view for a single movie or series."""
    movie = get_object_or_404(Movie, pk=pk)
    
    # Get similar movies based on genres
    similar_movies = Movie.objects.filter(
        genres__in=movie.genres.all()
    ).exclude(pk=movie.pk).distinct()[:10]
    
    # Check if the movie is in the user's watchlist
    in_my_list = False
    if 'profile_id' in request.session:
        in_my_list = MyList.objects.filter(
            profile_id=request.session['profile_id'],
            movie=movie
        ).exists()
    
    # Get user rating if logged in
    user_rating = None
    if request.user.is_authenticated and 'profile_id' in request.session:
        try:
            user_rating = Rating.objects.get(
                movie=movie,
                profile_id=request.session['profile_id']
            ).rating
        except Rating.DoesNotExist:
            pass
    
    context = {
        'movie': movie,
        'similar_movies': similar_movies,
        'in_my_list': in_my_list,
        'user_rating': user_rating,
    }
    
    if movie.is_series:
        # Add seasons and episodes for TV series
        seasons = Season.objects.filter(series=movie).order_by('season_number')
        context['seasons'] = seasons
    
    return render(request, 'movies/movie_detail.html', context)

def watch_movie(request, pk):
    """View for watching a movie or episode."""
    if 'profile_id' not in request.session:
        messages.warning(request, 'Please select a profile first.')
        return redirect('profile_list')
    
    movie = get_object_or_404(Movie, pk=pk)
    
    # Update or create watch history
    watch_history, created = WatchHistory.objects.get_or_create(
        profile_id=request.session['profile_id'],
        movie=movie,
        defaults={'progress': 0.0}
    )
    
    context = {
        'movie': movie,
        'watch_history': watch_history,
    }
    
    return render(request, 'movies/watch.html', context)

def search_movies(request):
    """Search for movies and TV shows."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home')
    
    # Search in title, description, and genres
    results = Movie.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(genres__name__icontains=query)
    ).distinct()
    
    # Filter by content type if specified
    content_type = request.GET.get('type', '')
    if content_type in ['movie', 'series', 'documentary']:
        results = results.filter(content_type=content_type)
    
    # Pagination
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'results': page_obj,
        'result_count': paginator.count,
        'content_type': content_type,
    }
    
    return render(request, 'movies/search_results.html', context)

def browse_by_genre(request, genre_name):
    """Browse movies by genre."""
    genre = get_object_or_404(Genre, name__iexact=genre_name)
    
    # Filter movies by genre
    movies = Movie.objects.filter(genres=genre).order_by('-release_date')
    
    # Pagination
    paginator = Paginator(movies, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'genre': genre,
        'movies': page_obj,
    }
    
    return render(request, 'movies/genre_detail.html', context)

@login_required
@require_POST
def rate_movie(request, movie_id):
    """Rate a movie or update existing rating."""
    if 'profile_id' not in request.session:
        return JsonResponse({'status': 'error', 'message': 'No profile selected'}, status=400)
    
    movie = get_object_or_404(Movie, id=movie_id)
    rating_value = int(request.POST.get('rating', 0))
    
    if not 1 <= rating_value <= 5:
        return JsonResponse({'status': 'error', 'message': 'Invalid rating'}, status=400)
    
    # Update or create rating
    rating, created = Rating.objects.update_or_create(
        movie=movie,
        profile_id=request.session['profile_id'],
        defaults={'rating': rating_value}
    )
    
    return JsonResponse({
        'status': 'success', 
        'message': 'Rating saved',
        'rating': rating_value,
        'is_new': created
    })
