from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('search/', views.search_movies, name='search_movies'),
    
    # Movie/Series detail pages
    path('movie/<int:pk>/<slug:slug>/', views.movie_detail, name='movie_detail'),
    path('watch/<int:pk>/', views.watch_movie, name='watch_movie'),
    
    # Genres
    path('genre/<str:genre_name>/', views.browse_by_genre, name='browse_genre'),
    
    # API endpoints
    path('api/rate/<int:movie_id>/', views.rate_movie, name='rate_movie'),
]
