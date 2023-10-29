from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/thread/(?P<note_title>\w+)/$", consumers.ThreadConsumer.as_asgi()),
]
