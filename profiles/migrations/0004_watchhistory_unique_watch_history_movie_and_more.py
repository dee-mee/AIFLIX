# Generated by Django 5.0.7 on 2025-06-28 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("movies", "0008_add_video_file_field"),
        ("profiles", "0003_fix_profile_primary_key"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="watchhistory",
            constraint=models.UniqueConstraint(
                condition=models.Q(("episode__isnull", True)),
                fields=("profile", "movie"),
                name="unique_watch_history_movie",
            ),
        ),
        migrations.AddConstraint(
            model_name="watchhistory",
            constraint=models.UniqueConstraint(
                condition=models.Q(("movie__isnull", True)),
                fields=("profile", "episode"),
                name="unique_watch_history_episode",
            ),
        ),
    ]
