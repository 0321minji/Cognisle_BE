"""
WSGI config for Cognisle project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'Cognisle.settings.production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cognisle.settings.production')
elif os.environ.get('DJANGO_SETTINGS_MODULE') == 'Cognisle.settings.development':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cognisle.settings.development')
    
application = get_wsgi_application()
