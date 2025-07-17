from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/query-progress/(?P<session_id>[\w-]+)/?$', consumers.QueryProgressConsumer.as_asgi())
]