from django.urls import path
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from . import views
from . import ai_views

app_name = 'movies'

urlpatterns = [
    # Home page (protected, redirects to login if not authenticated)
    path('home/', views.home, name='home'),
    
    # Redirect root to landing page for guests, home for authenticated users
    path('', views.landing_redirect, name='root_redirect'),
    
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
    
    # AI Content Categories
    path('browse/ai/', login_required(ai_views.AIHomeView.as_view()), name='ai_home'),
    path('browse/ai/ai-generated/', 
         login_required(ai_views.AICategoryView.as_view()), 
         name='ai_generated'),
    path('browse/ai/ai-upscaled/', 
         login_required(ai_views.AICategoryView.as_view()), 
         name='ai_upscaled'),
    path('browse/ai/user-created/', 
         login_required(ai_views.AICategoryView.as_view()), 
         name='user_created'),
    path('browse/ai/ai-series/', 
         login_required(ai_views.AICategoryView.as_view()), 
         name='ai_series'),
    path('browse/ai/<str:category_slug>/', 
         login_required(ai_views.AICategoryView.as_view()), 
         name='ai_category'),
    path('browse/ai/movie/<int:movie_id>/', 
         login_required(ai_views.ai_movie_detail), 
         name='ai_movie_detail'),
]
