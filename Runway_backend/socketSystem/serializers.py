from rest_framework import serializers
from hubs.serializer import HubSerializer
# from auths.models import 
from socketSystem.models import Notification,Message
# ,Chat,
# ,ChatMessage
# Message, MessageMedia,
from auths.serializer import UserSerializer


        
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        

        

class MessageSerializer(serializers.ModelSerializer):
    sender=UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = '__all__'
        
class MessageChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

        
        
        

        