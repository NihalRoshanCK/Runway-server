from rest_framework import viewsets
from socketSystem.models import Notification,Message
from socketSystem.serializers import NotificationSerializer,MessageSerializer
from rest_framework import permissions
from rest_framework.response import Response
from auths.utilties import IsStaff

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    
class MessageViewSet(viewsets.ModelViewSet):
    queryset=Message.objects.all()
    serializer_class=MessageSerializer
    permission_classes=[IsStaff]

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(hub=request.user.staff.hub)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    