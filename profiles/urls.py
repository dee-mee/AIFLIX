from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.profile_list, name='profile_list'),
    path('create/', views.create_profile, name='create_profile'),
    path('select/<int:profile_id>/', views.select_profile, name='select_profile'),
    path('my-list/', views.my_list, name='my_list'),
    path('toggle-my-list/<int:movie_id>/', views.toggle_my_list, name='toggle_my_list'),
    path('delete/<int:profile_id>/', views.delete_profile, name='delete_profile'),
]
