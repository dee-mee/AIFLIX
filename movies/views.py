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

def browse(request):
    """Browse all available content with filtering options."""
    # Get filter parameters
    genre_slug = request.GET.get('genre')
    content_type = request.GET.get('content_type')  # 'movie' or 'series'
    sort_by = request.GET.get('sort', 'latest')  # 'latest', 'trending', 'popular', 'rating'
    
    # Start with base queryset
    movies = get_base_queryset()
    
    # Apply content type filter
    if content_type in ['movie', 'series']:
        movies = movies.filter(content_type=content_type)
    
    # Apply genre filter if provided
    selected_genre = None
    if genre_slug:
        try:
            selected_genre = Genre.objects.get(slug=genre_slug)
            movies = movies.filter(genres=selected_genre)
        except Genre.DoesNotExist:
            pass
    
    # Apply sorting
    if sort_by == 'title':
        movies = movies.order_by('title')
    elif sort_by == 'trending':
        movies = movies.filter(is_trending=True).order_by('-release_date')
    elif sort_by == 'popular':
        movies = movies.order_by('-imdb_rating')
    elif sort_by == 'rating':
        movies = movies.order_by('-imdb_rating', '-release_date')
    else:  # latest
        movies = movies.order_by('-release_date')
    
    # Get all genres for filter sidebar
    all_genres = Genre.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(movies, 20)  # Show 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'movies': page_obj,
        'page_obj': page_obj,
        'all_genres': all_genres,
        'selected_genre': selected_genre,
        'content_type': content_type,
        'sort_by': sort_by,
        'is_paginated': page_obj.has_other_pages(),
    }
    return render(request, 'movies/browse.html', context)

def tv_shows(request):
    """TV Shows landing page with featured and trending TV shows."""
    # Get featured TV show (most recent trending show)
    featured_show = get_base_queryset().filter(
        content_type='series',
        is_trending=True
    ).order_by('-release_date').first()
    
    # If no trending show, get the most recent show
    if not featured_show:
        featured_show = get_base_queryset().filter(
            content_type='series'
        ).order_by('-release_date').first()
    
    # Get trending shows (excluding the featured one)
    trending_shows = get_base_queryset().filter(
        content_type='series',
        is_trending=True
    ).exclude(id=featured_show.id if featured_show else None)[:10]
    
    # Get popular shows (by IMDB rating)
    popular_shows = get_base_queryset().filter(
        content_type='series'
    ).order_by('-imdb_rating')[:10]
    
    # Get new releases (latest 10 shows)
    new_releases = get_base_queryset().filter(
        content_type='series'
    ).order_by('-release_date')[:10]
    
    # Annotate with latest season and episode count
    from django.db.models import Max, Count
    new_releases = new_releases.annotate(
        latest_season=Max('seasons__season_number'),
        episode_count=Count('seasons__episodes')
    )
    
    # Get all genres for TV shows
    from django.db.models import Count
    genres = Genre.objects.filter(
        movies__content_type='series'
    ).distinct().annotate(
        num_shows=Count('movies', filter=Q(movies__content_type='series'))
    ).order_by('-num_shows')
    
    context = {
        'featured_show': featured_show,
        'trending_shows': trending_shows,
        'popular_shows': popular_shows,
        'new_releases': new_releases,
        'genres': genres,
    }
    return render(request, 'movies/tv_shows.html', context)

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
        ).order_by('-is_trending', '-release_date')[:10]
    else:
        trending_movies = base_queryset.order_by('-release_date')[:10]
    
    # Popular content (based on ratings and release date)
    popular_movies = base_queryset.order_by(
        '-imdb_rating',  # Sort by IMDB rating (highest first)
        '-release_date'  # Then by newest first
    )[:10]
    
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
        num_movies=Count('movies', filter=Q(movies__is_active=True))
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
        return redirect('movies:home')
    
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
