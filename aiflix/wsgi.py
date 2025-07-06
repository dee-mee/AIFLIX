"""
WSGI config for aiflix project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiflix.settings')

# Initialize Django application
application = get_wsgi_application()

# Wrap with WhiteNoise for static files
application = WhiteNoise(application)

# Add static files configuration
application.add_files(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'), prefix='static/')
