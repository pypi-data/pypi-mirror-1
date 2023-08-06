from django.conf import settings
from django.contrib.sites.models import Site

MONETARY_LOCALE = getattr(settings, 'MONETARY_LOCALE', '')
STATIC_FILES_PATH = getattr(settings, 'STATIC_FILES_PATH', 'uploads')

ROBOT_PROTECTION_DOMAIN = getattr(settings, 'ROBOT_PROTECTION_DOMAIN', None)

