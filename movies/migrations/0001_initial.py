# Generated by Django 5.0.7 on 2025-06-26 12:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Episode",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("episode_number", models.IntegerField()),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("thumbnail", models.ImageField(upload_to="episode_thumbnails/")),
                (
                    "video_file",
                    models.FileField(blank=True, null=True, upload_to="episodes/"),
                ),
                ("video_url", models.URLField(blank=True, null=True)),
                ("duration", models.IntegerField(help_text="Duration in minutes")),
                ("air_date", models.DateField()),
            ],
            options={
                "ordering": ["season", "episode_number"],
            },
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                ("slug", models.SlugField(blank=True, unique=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Season",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("season_number", models.IntegerField()),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("release_date", models.DateField()),
                (
                    "poster",
                    models.ImageField(
                        blank=True, null=True, upload_to="season_posters/"
                    ),
                ),
            ],
            options={
                "ordering": ["series", "season_number"],
            },
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=200, unique=True)),
                ("description", models.TextField()),
                ("thumbnail", models.ImageField(upload_to="thumbnails/")),
                (
                    "banner_image",
                    models.ImageField(blank=True, null=True, upload_to="banners/"),
                ),
                ("trailer_url", models.URLField(blank=True, null=True)),
                (
                    "video_file",
                    models.FileField(blank=True, null=True, upload_to="videos/"),
                ),
                ("video_url", models.URLField(blank=True, null=True)),
                ("duration", models.IntegerField(help_text="Duration in minutes")),
                ("release_date", models.DateField()),
                (
                    "content_type",
                    models.CharField(
                        choices=[
                            ("movie", "Movie"),
                            ("series", "TV Series"),
                            ("documentary", "Documentary"),
                        ],
                        default="movie",
                        max_length=20,
                    ),
                ),
                (
                    "maturity_rating",
                    models.CharField(
                        choices=[
                            ("G", "G - General Audiences"),
                            ("PG", "PG - Parental Guidance"),
                            ("PG-13", "PG-13 - Parents Strongly Cautioned"),
                            ("R", "R - Restricted"),
                            ("NC-17", "NC-17 - Adults Only"),
                            ("TV-Y", "TV-Y - All Children"),
                            ("TV-Y7", "TV-Y7 - Directed to Older Children"),
                            ("TV-G", "TV-G - General Audience"),
                            ("TV-PG", "TV-PG - Parental Guidance Suggested"),
                            ("TV-14", "TV-14 - Parents Strongly Cautioned"),
                            ("TV-MA", "TV-MA - Mature Audience Only"),
                        ],
                        default="PG",
                        max_length=10,
                    ),
                ),
                ("is_featured", models.BooleanField(default=False)),
                ("is_trending", models.BooleanField(default=False)),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this movie is active and should be shown on the site",
                    ),
                ),
                ("imdb_rating", models.FloatField(default=0.0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "genres",
                    models.ManyToManyField(related_name="movies", to="movies.genre"),
                ),
            ],
            options={
                "ordering": ["-release_date"],
            },
        ),
        migrations.CreateModel(
            name="Rating",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.IntegerField(
                        choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "movie",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ratings",
                        to="movies.movie",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
