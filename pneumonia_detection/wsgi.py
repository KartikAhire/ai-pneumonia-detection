"""
WSGI config for pneumonia_detection project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pneumonia_detection.settings')

application = get_wsgi_application()
