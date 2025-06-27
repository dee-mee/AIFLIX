from django.contrib import admin
from .models import Movie, Genre, Season, Episode, Rating

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'content_category', 'is_ai_generated', 'release_date', 'is_featured')
    list_filter = ('content_type', 'content_category', 'is_ai_generated', 'genres', 'release_date')
    search_fields = ('title', 'description', 'ai_model_used')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'content_type', 'content_category')
        }),
        ('AI Generation', {
            'fields': ('is_ai_generated', 'ai_model_used', 'generation_parameters', 
                     'original_quality', 'upscale_technique'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('thumbnail', 'banner_image', 'trailer_url', 'video_file', 'video_url')
        }),
        ('Metadata', {
            'fields': ('release_date', 'duration', 'genres', 'maturity_rating', 
                     'is_featured', 'created_at', 'updated_at')
        }),
    )

class SeasonInline(admin.TabularInline):
    model = Season
    extra = 1
    show_change_link = True
    fields = ('season_number', 'title', 'release_date', 'poster')

class EpisodeInline(admin.StackedInline):
    model = Episode
    extra = 1
    fields = ('episode_number', 'title', 'description', 'thumbnail', 'video_file', 'video_url', 'duration', 'air_date')

class SeasonAdmin(admin.ModelAdmin):
    list_display = ('title', 'series', 'season_number', 'release_date')
    list_filter = ('series', 'release_date')
    search_fields = ('title', 'description')
    inlines = [EpisodeInline]

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'season', 'episode_number', 'air_date', 'duration')
    list_filter = ('season__series', 'season', 'air_date')
    search_fields = ('title', 'description')
    list_select_related = ('season', 'season__series')

class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'profile', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('movie__title', 'profile__name')
    list_select_related = ('movie', 'profile')

# Register your models here
admin.site.register(Genre, GenreAdmin)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Episode, EpisodeAdmin)
admin.site.register(Rating, RatingAdmin)
