from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Genre(models.Model):
    """Genre model for categorizing movies and shows."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class Movie(models.Model):
    """Main model for both movies and TV series."""
    CONTENT_TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('series', 'TV Series'),
        ('documentary', 'Documentary'),
    ]
    
    MATURITY_RATING_CHOICES = [
        ('G', 'G - General Audiences'),
        ('PG', 'PG - Parental Guidance'),
        ('PG-13', 'PG-13 - Parents Strongly Cautioned'),
        ('R', 'R - Restricted'),
        ('NC-17', 'NC-17 - Adults Only'),
        ('TV-Y', 'TV-Y - All Children'),
        ('TV-Y7', 'TV-Y7 - Directed to Older Children'),
        ('TV-G', 'TV-G - General Audience'),
        ('TV-PG', 'TV-PG - Parental Guidance Suggested'),
        ('TV-14', 'TV-14 - Parents Strongly Cautioned'),
        ('TV-MA', 'TV-MA - Mature Audience Only'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='thumbnails/')
    banner_image = models.ImageField(upload_to='banners/', blank=True, null=True)
    trailer_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    release_date = models.DateField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='movie')
    maturity_rating = models.CharField(max_length=10, choices=MATURITY_RATING_CHOICES, default='PG')
    genres = models.ManyToManyField(Genre, related_name='movies')
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    imdb_rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('movie_detail', kwargs={'pk': self.pk, 'slug': self.slug})
    
    @property
    def is_series(self):
        return self.content_type == 'series'
    
    class Meta:
        ordering = ['-release_date']

class Season(models.Model):
    """Season model for TV series."""
    series = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='seasons')
    season_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    release_date = models.DateField()
    poster = models.ImageField(upload_to='season_posters/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.series.title} - Season {self.season_number}: {self.title}"
    
    class Meta:
        ordering = ['series', 'season_number']
        unique_together = ['series', 'season_number']

class Episode(models.Model):
    """Episode model for TV series episodes."""
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='episode_thumbnails/')
    video_file = models.FileField(upload_to='episodes/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    air_date = models.DateField()
    
    def __str__(self):
        return f"{self.season.series.title} S{self.season.season_number:02d}E{self.episode_number:02d}: {self.title}"
    
    class Meta:
        ordering = ['season', 'episode_number']
        unique_together = ['season', 'episode_number']

class Rating(models.Model):
    """User ratings for movies and shows."""
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    profile = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 star rating
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['movie', 'profile']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.profile.name} rated {self.movie.title} {self.rating} stars"
