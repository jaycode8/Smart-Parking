from django.urls import re_path
from .socket import WebSocket

websocket_urlpatterns = [
    re_path(r'ws/updates/$', WebSocket.as_asgi()),
]
