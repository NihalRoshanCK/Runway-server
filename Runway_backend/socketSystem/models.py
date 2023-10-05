from django.db import models
from hubs.models import Hub
from auths.models import CustomUser,Staff
from django.contrib.auth import get_user_model


class NotificationContent(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.ForeignKey(NotificationContent, on_delete=models.CASCADE)
    is_seen=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"user: {self.user}message: {self.content.message}"


class MessageMedia(models.Model):
    media = models.FileField(upload_to='media/', null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
class Message(models.Model):
    hub = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    media = models.ForeignKey(MessageMedia, on_delete=models.CASCADE, null=True, blank=True)
    message_type = models.CharField(choices=[('text', 'Text'), ('audio', 'Audio'), ('video', 'Video')], max_length=10)
    seen_by_staff = models.ManyToManyField(Staff, blank=True)
    
    def save(self, *args, **kwargs):
        # Automatically add the sender to seen_by_staff when saving the message
        if self.sender and self.sender.staff:
            super().save(*args, **kwargs)  # Save the message first
            self.seen_by_staff.add(self.sender.staff)
        else:
            super().save(*args, **kwargs)






    
    
    
    
    
    











    
    
    
# class Chat(models.Model):
#     hub_gropup = models.ManyToManyField(Staff, related_name='chats')

# class Message(models.Model):
#     chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
#     sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     message_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('audio', 'Audio'), ('video', 'Video')])
#     file = models.FileField(upload_to='message_files/', null=True, blank=True)  # Specify the upload path

#     class Meta:
#         ordering = ['-timestamp']
    
# class ChatMessage(models.Model):
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
#     hub = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name='chat_messages')
#     message_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('audio', 'Audio'), ('video', 'Video')])
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     file = models.FileField(upload_to='message_files/', null=True, blank=True)  # Specify the upload path

#     def __str__(self):
#         return f'{self.sender} - {self.timestamp}'
    
    
# class Message(models.Model):
#     MESSAGE_TYPE = [('text', 'text'), ('image', 'image'), ('video', 'video'), ('audio', 'audio'), ('file', 'file')]

#     text = models.CharField(max_length=100, null=True, blank=True)
#     type = models.CharField(max_length=30, choices=MESSAGE_TYPE, default='text')
#     media = models.ForeignKey(to='MessageMedia', on_delete=models.CASCADE, null=True, blank=True)
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sended_messages')
#     receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_messages')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.sender} to {self.receiver} at {self.created_at}'


# class MessageMedia(models.Model):
#     media = models.FileField(upload_to='media/', null=False, blank=False)
    
# class Message(models.Model):
#     MESSAGE_TYPE = [('text', 'Text'), ('audio', 'Audio'), ('video', 'Video'), ('image', 'Image'), ('file', 'File')]

#     text = models.CharField(max_length=100, null=True, blank=True)
#     type = models.CharField(max_length=30, choices=MESSAGE_TYPE, default='text')
#     media = models.FileField(upload_to='media/', null=True, blank=True)
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
#     group = models.ForeignKey('Group', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.sender.user.username} ({self.get_type_display()})'

# class Group(models.Model):
#     name = models.CharField(max_length=100)
#     members = models.ManyToManyField(CustomUser, related_name='group_memberships')

#     def __str__(self):
#         return self.name


# class Message(models.Model):
#     sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
#     hub = models.ForeignKey(Hub, on_delete=models.CASCADE, related_name='chat_messages')
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     message_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('audio', 'Audio'), ('video', 'Video')])

#     def __str__(self):
#         return f"{self.sender.email} - {self.timestamp}"