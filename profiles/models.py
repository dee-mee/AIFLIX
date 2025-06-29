from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()

class Profile(models.Model):
    """User profile model for multiple viewing profiles."""
    MATURITY_CHOICES = [
        ('all', 'All Ages'),
        ('7+', '7+'),
        ('13+', '13+'),
        ('16+', '16+'),
        ('18+', '18+'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    name = models.CharField(max_length=50)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_kids = models.BooleanField(default=False)
    maturity_level = models.CharField(max_length=3, choices=MATURITY_CHOICES, default='all')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s profile: {self.name}"
        
    def get_avatar_url(self):
        """Return the URL for the profile's avatar, with fallback to default avatars."""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
            
        # Default avatar based on profile type
        if self.is_kids:
            return '/static/images/avatars/kids/avatar1.png'  # Default kids avatar
        return '/static/images/default-avatar.png'  # Default regular avatar
        
    def is_kids_profile(self):
        """Helper method to check if this is a kids profile."""
        return self.is_kids
        
    def get_allowed_maturity_levels(self):
        """Return a list of maturity levels allowed for this profile."""
        if self.is_kids:
            return ['all', '7+']
            
        # For non-kids profiles, return all levels up to and including their set level
        levels = ['all', '7+', '13+', '16+', '18+']
        if self.maturity_level in levels:
            return levels[:levels.index(self.maturity_level) + 1]
        return levels  # Fallback to all levels

class WatchHistory(models.Model):
    """Tracks what content a profile has watched."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, null=True, blank=True)
    episode = models.ForeignKey('movies.Episode', on_delete=models.CASCADE, null=True, blank=True)
    watched_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    completed = models.BooleanField(default=False)
    
    def clean(self):
        if not self.movie and not self.episode:
            raise ValidationError('Either movie or episode must be set')
        if self.movie and self.episode:
            raise ValidationError('Cannot set both movie and episode')
        super().clean()
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'movie'],
                condition=Q(episode__isnull=True),
                name='unique_watch_history_movie'
            ),
            models.UniqueConstraint(
                fields=['profile', 'episode'],
                condition=Q(movie__isnull=True),
                name='unique_watch_history_episode'
            )
        ]
        verbose_name_plural = 'Watch History'
        ordering = ['-watched_at']

class MyList(models.Model):
    """User's saved content to watch later."""
    CONTENT_TYPES = [
        ('movie', 'Movie'),
        ('series', 'TV Series'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='my_list')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='movie')
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, null=True, blank=True)
    series = models.ForeignKey('movies.Movie', on_delete=models.CASCADE, related_name='series_in_list', null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'My List'
        unique_together = [
            ['profile', 'movie'],
            ['profile', 'series'],
        ]
        ordering = ['-added_at']

    def __str__(self):
        content = self.movie if self.movie else self.series
        return f"{self.profile.name}'s list: {content.title}"
        
    def save(self, *args, **kwargs):
        # Ensure only one of movie or series is set
        if self.movie and self.series:
            raise ValueError("Cannot set both movie and series")
        if not self.movie and not self.series:
            raise ValueError("Either movie or series must be set")
            
        # Set content_type based on which field is set
        if self.movie:
            self.content_type = 'movie' if not self.movie.is_series else 'series'
            self.series = None if not self.movie.is_series else self.movie
        elif self.series:
            self.content_type = 'series'
            self.movie = None
            
        super().save(*args, **kwargs)
