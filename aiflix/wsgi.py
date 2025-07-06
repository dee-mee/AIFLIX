"""
WSGI config for aiflix project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aiflix.settings')

# Initialize Django application
application = get_wsgi_application()

# Configure WhiteNoise for static files
application = WhiteNoise(application)

# Add static files directories
application.add_files(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'), prefix='static/')
application.add_files(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static_new'), prefix='static_new/')

# Configure port binding
PORT = config('PORT', default='8000')
if os.environ.get('RENDER'):
    PORT = config('PORT', default='10000')
