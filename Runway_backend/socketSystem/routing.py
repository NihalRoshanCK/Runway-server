from django.urls import path,re_path

from socketSystem.consumers import NotificationConsumer,ChatConsumer
# ,ChatConsumer
# ChatConsumer
# MessageConsumer,

websocket_urlpatterns = [
    # path('ws/chat/<str:group_name>/', ChatConsumer.as_asgi()),
    # path('ws/messages/', MessageConsumer.as_asgi(), name='messages'),
    # re_path(r"ws/chat/(?P<hub_id>\d+)/$", ChatConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<chat_id>\d+)/$',ChatConsumer.as_asgi()),
    path('ws/messaging/', ChatConsumer.as_asgi()),
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]