from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'movies'

# Redirect old root URLs to the new /browse/ paths
urlpatterns = [
    # Redirect old root paths to /browse/
    path('', RedirectView.as_view(url='/browse/', permanent=True)),
    
    # Main pages under /browse/
    path('browse/', views.browse, name='browse'),
    path('browse/tv-shows/', views.tv_shows, name='tv_shows'),
    path('browse/movies/', views.movies, name='movies'),
    path('browse/new-popular/', views.new_popular, name='new_popular'),
    path('browse/search/', views.search_movies, name='search_movies'),
    
    # Movie/Series detail pages
    path('browse/movie/<int:pk>/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('browse/watch/<int:pk>/', views.watch_movie, name='watch_movie'),
    
    # Genres
    path('browse/genre/<str:genre_name>/', views.browse_by_genre, name='browse_genre'),
    
    # API endpoints (keep at root for backward compatibility)
    path('api/rate/<int:movie_id>/', views.rate_movie, name='rate_movie'),
]
