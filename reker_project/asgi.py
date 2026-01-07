# """
# ASGI config for reker_project project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reker_project.settings')

# application = get_asgi_application()

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "reker_project.settings")

django_asgi_app = get_asgi_application()

import realtime.routing  # AFTER settings set

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(
        realtime.routing.websocket_urlpatterns
    ),
})
