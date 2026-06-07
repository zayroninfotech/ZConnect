import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zconnect.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from messaging.routing import websocket_urlpatterns as chat_ws
from calls.routing import websocket_urlpatterns as call_ws

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(chat_ws + call_ws)
        )
    ),
})
