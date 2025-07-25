from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F, Case, When, Value, IntegerField
from django.contrib import messages
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

def new_popular(request):
    """New & Popular page with trending, popular, and upcoming content."""
    # Get trending content (movies and shows)
    trending = get_base_queryset().filter(
        is_trending=True
    ).order_by('-release_date')[:20]
    
    # Get popular content (by IMDB rating)
    popular = get_base_queryset().order_by('-imdb_rating')[:20]
    
    # Get new releases (released in the last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    new_releases = get_base_queryset().filter(
        release_date__gte=thirty_days_ago
    ).order_by('-release_date')[:20]
    
    # Get coming soon content (release date in the future)
    coming_soon = get_base_queryset().filter(
        release_date__gt=datetime.now()
    ).order_by('release_date')[:20]
    
    context = {
        'trending': trending,
        'popular': popular,
        'new_releases': new_releases,
        'coming_soon': coming_soon,
    }
    return render(request, 'movies/new_popular.html', context)

def movies(request):
    """Movies landing page with featured and trending movies."""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Get featured movie (trending or latest)
    featured_movie = get_base_queryset().filter(
        content_type='movie',
        is_trending=True
    ).exclude(id__isnull=True).order_by('-release_date').first()
    
    if not featured_movie:
        featured_movie = get_base_queryset().filter(
            content_type='movie'
        ).exclude(id__isnull=True).order_by('-release_date').first()
    
    # Get base querysets (without slicing)
    base_queryset = get_base_queryset()
    
    # Get trending movies (excluding featured)
    trending = base_queryset.filter(
        content_type='movie',
        is_trending=True,
        id__isnull=False
    ).exclude(id=featured_movie.id if featured_movie else None)
    
    # Get latest releases
    latest = base_queryset.filter(
        content_type='movie',
        id__isnull=False
    )
    
    # Get top rated movies
    top_rated = base_queryset.filter(
        content_type='movie',
        imdb_rating__isnull=False,
        id__isnull=False
    )
    
    # Get action movies (example genre)
    action_movies = base_queryset.filter(
        content_type='movie',
        genres__name__icontains='action',
        id__isnull=False
    ).distinct()
    
    # Get all genres for filter
    from .models import Genre
    genres = Genre.objects.filter(
        movies__content_type='movie'
    ).distinct().annotate(
        num_movies=Count('movies')
    ).order_by('-num_movies')
    
    # Apply genre filter if specified
    genre_filter = request.GET.get('genre')
    if genre_filter:
        trending = trending.filter(genres__slug=genre_filter)
        latest = latest.filter(genres__slug=genre_filter)
        top_rated = top_rated.filter(genres__slug=genre_filter)
    
    # Apply sorting to trending
    sort_by = request.GET.get('sort', 'trending')
    if sort_by == 'latest':
        trending = trending.order_by('-release_date')
    elif sort_by == 'rating':
        trending = trending.order_by('-imdb_rating')
    elif sort_by == 'year':
        trending = trending.order_by('-release_date__year', '-imdb_rating')
    elif sort_by == 'title':
        trending = trending.order_by('title')
    else:  # default trending sort
        trending = trending.order_by('-is_featured', '-release_date')
    
    # Apply ordering and slicing to other querysets
    latest = latest.order_by('-release_date')[:12]
    top_rated = top_rated.order_by('-imdb_rating')[:12]
    action_movies = action_movies[:12]
    
    context = {
        'featured_movie': featured_movie,
        'trending': trending,
        'latest': latest,
        'top_rated': top_rated,
        'action_movies': action_movies,
        'genres': genres,
    }
    return render(request, 'movies/movies.html', context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def landing_redirect(request):
    """Redirect to landing page for guests, home for authenticated users."""
    if request.user.is_authenticated:
        return redirect('movies:home')
    return redirect('landing')

@login_required
def home(request):
    """Authenticated user's home page with featured and trending movies."""
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    import logging
    
    logger = logging.getLogger(__name__)
    
    from django.conf import settings
    import os
    from .models import Movie  # Import Movie model directly
    
    # Debug: Get all movies with banner images directly from the Movie model
    # Bypass any custom manager or queryset filtering
    all_movies = list(Movie.objects.raw('SELECT * FROM movies_movie WHERE banner_image != ""'))
    logger.info(f"Raw SQL query found {len(all_movies)} movies with banners")
    
    try:
        # Get all movies with banner images, ordered by release date (newest first)
        featured_movies = sorted(
            [m for m in all_movies if hasattr(m, 'release_date')],
            key=lambda x: x.release_date,
            reverse=True
        )[:5]
        
        logger.info(f"Found {len(featured_movies)} movies with banners")
        
        # Log movie titles safely
        if featured_movies:
            movie_titles = []
            for movie in featured_movies:
                try:
                    title = getattr(movie, 'title', 'No title')
                    movie_titles.append(title)
                    
                    # Debug banner information
                    if hasattr(movie, 'banner_image') and movie.banner_image:
                        try:
                            banner_path = os.path.join(settings.MEDIA_ROOT, str(movie.banner_image))
                            logger.info(f"  - {title}: {movie.banner_image.url}")
                            logger.info(f"    Full path: {banner_path}")
                            logger.info(f"    Exists: {os.path.exists(banner_path)}")
                        except Exception as e:
                            logger.error(f"Error checking banner for {title}: {str(e)}")
                except Exception as e:
                    logger.error(f"Error processing movie: {str(e)}")
            
            logger.info(f"Movies with banners: {movie_titles}")
        else:
            logger.warning("No movies with banners found in the database")
    except Exception as e:
        logger.error(f"Error processing featured movies: {str(e)}")
        featured_movies = []
    
    # If still no movies with banners, try to get any movie with a thumbnail
    if not featured_movies:
        logger.warning("No movies with banners found, falling back to thumbnails")
        featured_movies = list(Movie.objects.filter(
            thumbnail__isnull=False
        ).order_by('-release_date')[:5])
        
        if featured_movies:
            logger.info(f"Found {len(featured_movies)} movies with thumbnails to use as fallback")
    
    # Ensure we have a list
    if not isinstance(featured_movies, list):
        featured_movies = list(featured_movies) if featured_movies else []
    
    # If not enough movies, fill with latest movies
    if len(featured_movies) < 5:
        existing_ids = [m.id for m in featured_movies] if featured_movies else []
        additional_count = 5 - len(featured_movies)
        
        additional_movies = list(get_base_queryset().filter(
            content_type='movie',
            banner_image__isnull=False
        ).exclude(id__in=existing_ids).order_by('-release_date')[:additional_count])
        
        featured_movies.extend(additional_movies)
        logger.info(f"Added {len(additional_movies)} additional movies, total now: {len(featured_movies)}")
    
    # Get the first featured movie as the default
    featured_movie = featured_movies[0] if featured_movies else None
    
    # Get trending movies (excluding featured)
    trending = get_base_queryset().filter(
        content_type='movie',
        is_trending=True,
        id__isnull=False
    ).exclude(id__in=[m.id for m in featured_movies] if featured_movies else [])[:12]
    
    # Get latest releases
    latest = get_base_queryset().filter(
        content_type='movie',
        id__isnull=False
    ).order_by('-release_date')[:12]
    
    # Get top rated movies
    top_rated = get_base_queryset().filter(
        content_type='movie',
        imdb_rating__isnull=False,
        id__isnull=False
    ).order_by('-imdb_rating')[:12]
    
    # Get action movies (example genre)
    action_movies = get_base_queryset().filter(
        content_type='movie',
        genres__name__icontains='action',
        id__isnull=False
    ).distinct()[:12]
    
    # Get all genres for filter
    from .models import Genre
    genres = Genre.objects.filter(
        movies__content_type='movie'
    ).distinct().annotate(
        num_movies=Count('movies')
    ).order_by('-num_movies')
    
    # Apply genre filter if specified
    genre_filter = request.GET.get('genre')
    if genre_filter:
        trending = trending.filter(genres__slug=genre_filter)
        latest = latest.filter(genres__slug=genre_filter)
        top_rated = top_rated.filter(genres__slug=genre_filter)
    
    # Apply sorting
    sort_by = request.GET.get('sort', 'trending')
    if sort_by == 'latest':
        trending = trending.order_by('-release_date')
    elif sort_by == 'rating':
        trending = trending.order_by('-imdb_rating')
    elif sort_by == 'year':
        trending = trending.order_by('-release_date__year', '-imdb_rating')
    elif sort_by == 'title':
        trending = trending.order_by('title')
    
    # Ensure featured_movies is a list of movie objects
    if featured_movies is None:
        featured_movies = []
    elif not isinstance(featured_movies, list):
        try:
            featured_movies = list(featured_movies)
        except (TypeError, ValueError):
            featured_movies = []
    
    # Debug information
    logger.info(f"Preparing to render home page with {len(featured_movies)} featured movies")
    for i, movie in enumerate(featured_movies, 1):
        logger.info(f"  {i}. {getattr(movie, 'title', 'No title')} - Banner: {getattr(movie, 'banner_image', 'No banner')}")
    
    # Debug authentication and session info
    logger.info(f"\n=== AUTHENTICATION DEBUG ===")
    logger.info(f"User authenticated: {request.user.is_authenticated}")
    logger.info(f"User: {request.user}")
    logger.info(f"Session keys: {list(request.session.keys())}")
    logger.info(f"Profile in session: {request.session.get('profile_id')}")
    logger.info("=== END AUTHENTICATION DEBUG ===\n")
    
    # Get continue watching - movies and episodes that are not completed
    continue_watching = []
    if request.user.is_authenticated and hasattr(request.user, 'profiles'):
        try:
            logger.info(f"\n=== DEBUG: Continue Watching Debug ===")
            logger.info(f"User: {request.user}")
            logger.info(f"Has profiles attribute: {hasattr(request.user, 'profiles')}")
            
            profiles = list(request.user.profiles.all())
            logger.info(f"Found {len(profiles)} profiles: {profiles}")
            
            if not profiles:
                logger.warning("No profiles found for user")
                
            profile = request.user.profiles.first()
            if profile:
                logger.info(f"Using profile: {profile.id} - {profile.name}")
                
                # Get movies that are in progress
                in_progress_movies = WatchHistory.objects.filter(
                    profile=profile,
                    movie__isnull=False,
                    progress__gt=0,
                    progress__lt=90,
                    completed=False
                ).select_related('movie').order_by('-watched_at')
                
                movie_count = in_progress_movies.count()
                logger.info(f"Found {movie_count} in-progress movies")
                if movie_count > 0:
                    for m in in_progress_movies:
                        logger.info(f"  - Movie: {m.movie.title if m.movie else 'No movie'}, ID: {m.movie.id if m.movie else 'N/A'}, Progress: {m.progress}%, Watched: {m.watched_at}")
                else:
                    logger.info("  No in-progress movies found")
                
                # Get episodes that are in progress
                in_progress_episodes = WatchHistory.objects.filter(
                    profile=profile,
                    episode__isnull=False,
                    progress__gt=0,
                    progress__lt=90,
                    completed=False
                ).select_related('episode', 'episode__season', 'episode__season__series').order_by('-watched_at')
                
                episode_count = in_progress_episodes.count()
                logger.info(f"Found {episode_count} in-progress episodes")
                if episode_count > 0:
                    for e in in_progress_episodes:
                        logger.info(f"  - Episode: {e.episode.title if e.episode else 'No episode'} "
                                    f"(ID: {e.episode.id if e.episode else 'N/A'}) "
                                    f"of {e.episode.season.series.title if e.episode and e.episode.season and e.episode.season.series else 'No show'} "
                                    f"(Season {e.episode.season.season_number if e.episode and e.episode.season else 'N/A'}, "
                                    f"Episode {e.episode.episode_number if e.episode else 'N/A'}), "
                                    f"Progress: {e.progress}%, Watched: {e.watched_at}")
                else:
                    logger.info("  No in-progress episodes found")
                
                # Combine and sort by last watched
                continue_watching = list(in_progress_movies) + list(in_progress_episodes)
                continue_watching.sort(key=lambda x: x.watched_at, reverse=True)
                continue_watching = continue_watching[:10]  # Limit to 10 items
                
                logger.info(f"\n=== Continue Watching Summary ===")
                logger.info(f"Total items: {len(continue_watching)}")
                
                if not continue_watching:
                    logger.info("No continue watching items to display")
                else:
                    for i, item in enumerate(continue_watching, 1):
                        if hasattr(item, 'movie') and item.movie:
                            logger.info(f"  {i}. [MOVIE] {item.movie.title} (ID: {item.movie.id}), Progress: {item.progress}%, Watched: {item.watched_at}")
                        elif hasattr(item, 'episode') and item.episode:
                            series_title = item.episode.season.series.title if item.episode.season and item.episode.season.series else 'Unknown Series'
                            logger.info(f"  {i}. [EPISODE] {item.episode.title} (ID: {item.episode.id}) of {series_title}, "
                                      f"S{item.episode.season.season_number:02d}E{item.episode.episode_number:02d}, "
                                      f"Progress: {item.progress}%, Watched: {item.watched_at}")
                
                logger.info("=== End Continue Watching Debug ===\n")
            else:
                logger.warning("No profile found for user")
        except Exception as e:
            logger.error(f"Error fetching continue watching: {str(e)}", exc_info=True)
    elif not request.user.is_authenticated:
        logger.warning("User is not authenticated")
    else:
        logger.warning("User has no profiles attribute")
    
    context = {
        'featured_movie': featured_movies[0] if featured_movies else None,
        'featured_movies': featured_movies,
        'trending': trending,
        'latest': latest,
        'top_rated': top_rated,
        'action_movies': action_movies,
        'genres': genres,
        'continue_watching': continue_watching,
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

def watch_movie(request, pk, episode_id=None):
    """View for watching a movie or episode."""
    if 'profile_id' not in request.session:
        messages.warning(request, 'Please select a profile first.')
        return redirect('profiles:profile_list')
    
    movie = get_object_or_404(Movie.objects.prefetch_related('seasons__episodes'), pk=pk)
    current_episode = None
    
    # If this is a series and an episode is specified, get the episode
    if movie.is_series and episode_id:
        try:
            current_episode = Episode.objects.select_related('season').get(
                id=episode_id,
                season__series=movie
            )
        except Episode.DoesNotExist:
            pass
    
    # Get or create watch history
    watch_history_kwargs = {
        'profile_id': request.session['profile_id'],
        'movie': movie,
    }
    
    if current_episode:
        watch_history_kwargs['episode'] = current_episode
    else:
        watch_history_kwargs['episode__isnull'] = True
    
    watch_history, created = WatchHistory.objects.get_or_create(
        **watch_history_kwargs,
        defaults={'progress': 0.0}
    )
    
    # Get user's rating for this movie
    user_rating = None
    try:
        rating_obj = Rating.objects.get(
            movie=movie,
            profile_id=request.session['profile_id']
        )
        user_rating = rating_obj.rating
    except Rating.DoesNotExist:
        pass
    
    context = {
        'movie': movie,
        'watch_history': watch_history,
        'user_rating': user_rating,
        'current_episode': current_episode,
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
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Rate movie endpoint hit. Method: {request.method}, Path: {request.path}")
    logger.info(f"Request data: {request.POST}")
    
    if 'profile_id' not in request.session:
        logger.warning("No profile_id in session")
        return JsonResponse({'status': 'error', 'message': 'No profile selected'}, status=400)
    
    try:
        movie = Movie.objects.get(id=movie_id)
        logger.info(f"Found movie: {movie.title}")
    except Movie.DoesNotExist:
        logger.error(f"Movie with id {movie_id} not found")
        return JsonResponse({'status': 'error', 'message': 'Movie not found'}, status=404)
        
    try:
        rating_value = int(request.POST.get('rating', 0))
        logger.info(f"Rating value: {rating_value}")
    except (TypeError, ValueError):
        logger.error("Invalid rating value")
        return JsonResponse({'status': 'error', 'message': 'Invalid rating value'}, status=400)
    
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
