from django.urls import path
from . import views
from .views import CreateProfileView
from . import views_manage

app_name = 'profiles'

urlpatterns = [
    # Profile selection and management
    path('', views.profile_list, name='profile_list'),
    path('select/<int:profile_id>/', views.select_profile, name='select_profile'),
    
    # Profile CRUD operations
    path('create/', CreateProfileView.as_view(), name='create'),
    path('manage/', views_manage.manage_profiles, name='manage'),
    path('edit/<int:pk>/', views_manage.EditProfileView.as_view(), name='edit'),
    path('delete/<int:pk>/', views_manage.DeleteProfileView.as_view(), name='delete'),
    path('set-default/<int:profile_id>/', views_manage.set_default_profile, name='set_default'),
    
    # User content
    path('my-list/', views.my_list, name='my_list'),
    path('toggle-my-list/<int:movie_id>/', views.toggle_my_list, name='toggle_my_list'),
    path('watch-history/update/<int:movie_id>/', views.update_watch_history, name='update_watch_history'),
]
