from rest_framework.serializers import ModelSerializer,ValidationError
from auths.models import CustomUser



class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'name',
            'profile_picture',
            'email',
            'password',
            # __all__
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data) 
        user.set_password(password)
        user.save()
        return user
    


