from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from django.templatetags.static import static
from .models import Movie, Genre

class LandingPageView(TemplateView):
    """Landing page view that serves as the new homepage."""
    template_name = 'landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
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
        
        context.update({
            'trending_movies': trending_movies,
            'featured_movie': featured_movie,
            'genres': genres,
            'placeholder_poster': static('img/placeholder-poster.jpg'),
            'hide_navbar': True,  # Hide default navbar
        })
        return context

def custom_404_view(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)
