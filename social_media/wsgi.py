"""
WSGI config for social_media project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""


import os
from static_ranges import Ranges
from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'social_media.settings')
application = Ranges(Cling(MediaCling(get_wsgi_application())))