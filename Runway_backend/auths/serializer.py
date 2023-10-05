from rest_framework.serializers import ModelSerializer
from django.contrib.auth import authenticate
from auths.models import CustomUser

class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ('id', 'email')
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, data):
        
        # For PATCH request, ensure users can only update their own data
        
        if self.context['request'].method == 'PATCH':
            if 'profile_picture' in data or 'number' in data:
                user = self.context['request'].user
                if not user.is_superuser:
                    if user.id != self.instance.id :
                        raise ValidationError("You are not allowed to update these fields.")
        return data