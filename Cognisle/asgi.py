"""
ASGI config for Cognisle project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'Cognisle.settings.production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cognisle.settings.production')
elif os.environ.get('DJANGO_SETTINGS_MODULE') == 'Cognisle.settings.development':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cognisle.settings.development')
    
application = get_asgi_application()
