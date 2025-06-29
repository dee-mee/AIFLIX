from django.db import migrations


def set_content_type(apps, schema_editor):
    MyList = apps.get_model('profiles', 'MyList')
    Movie = apps.get_model('movies', 'Movie')
    
    # Update existing records
    for item in MyList.objects.filter(content_type__isnull=True):
        if item.movie_id:
            movie = Movie.objects.get(id=item.movie_id)
            item.content_type = movie.content_type if movie.content_type in ['movie', 'series'] else 'movie'
            item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_alter_mylist_unique_together_mylist_content_type_and_more'),
        ('movies', '0001_initial'),  # Make sure this is the correct dependency
    ]

    operations = [
        migrations.RunPython(set_content_type, migrations.RunPython.noop),
    ]
