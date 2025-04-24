import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing  # Replace 'chat' with your app name if different
from whitenoise import WhiteNoise
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ProjectCore.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns  
        )
    ),
})

application = WhiteNoise(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))