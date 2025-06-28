from django.db import models
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

class WatchHistory(models.Model):
    """Tracks what content a profile has watched."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='watch_history')
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE)
    episode = models.ForeignKey('movies.Episode', on_delete=models.CASCADE, null=True, blank=True)
    watched_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    completed = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'movie', 'episode'],
                name='unique_watch_history'
            )
        ]

    class Meta:
        verbose_name_plural = 'Watch History'
        ordering = ['-watched_at']

class MyList(models.Model):
    """User's saved content to watch later."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='my_list')
    movie = models.ForeignKey('movies.Movie', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'My List'
        unique_together = ['profile', 'movie']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.profile.name}'s list: {self.movie.title}"
