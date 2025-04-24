import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application


# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjectCore.settings')
django.setup()

# Import your routing from the chat app
import chat.routing

# Main ASGI application
application = ProtocolTypeRouter({
    # HTTP requests are handled by Django as usual
    "http": get_asgi_application(),

    # WebSocket requests go through the AuthMiddlewareStack,
    # which adds `scope['user']` based on the session
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns  #  Must be a list of `re_path`
        )
    ),
})
