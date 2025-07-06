from django.shortcuts import render
from django.views import View
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.templatetags.static import static
from .models import Movie, Genre

class LandingPageView(View):
    """Landing page view that serves as the new homepage."""
    
    def get(self, request, *args, **kwargs):
        context = {
            'title': 'AIFLIX - Unlimited Movies & TV Shows'
        }
        
        # Get trending movies (using is_trending flag)
        trending_movies = Movie.objects.filter(
            is_trending=True,
            is_active=True
        ).order_by('-release_date')[:8]
        
        # Get featured movie (using is_featured flag)
        featured_movie = Movie.objects.filter(
            is_featured=True,
            is_active=True
        ).order_by('-release_date').first()
        
        # If no featured movie is marked, get the latest trending movie
        if not featured_movie and trending_movies.exists():
            featured_movie = trending_movies.first()
        
        # Get all genres for the browse section
        genres = Genre.objects.all()[:10]
        
        return render(request, 'landing.html', {
            'trending_movies': trending_movies,
            'featured_movie': featured_movie,
            'genres': genres,
            'hide_navbar': True,  # Hide default navbar
        })

def custom_404_view(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)
