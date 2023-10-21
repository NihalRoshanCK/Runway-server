from rest_framework import serializers
from auths.models import Staff,CustomUser
from hubs.models import Hub
from datetime import date
from rest_framework.exceptions import ValidationError


class OfficeStaffSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(write_only=True)
    address = serializers.CharField(write_only=True)
    joining_date = serializers.DateField(write_only=True)
    is_officeStaff = serializers.BooleanField(write_only=True)
    is_deleverystaff = serializers.BooleanField(write_only=True)
    is_hubadmin = serializers.BooleanField(write_only=True)
    hub = serializers.PrimaryKeyRelatedField(queryset=Hub.objects.all(), write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'profile_picture', 'email', 'password', 'age', 'address', 'joining_date', 'is_officeStaff', 'is_deleverystaff', 'is_hubadmin', 'hub']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        staff_data = {
            'age': validated_data.pop('age', None),
            'address': validated_data.pop('address', None),
            'joining_date': validated_data.pop('joining_date', None),
            'is_officeStaff': validated_data.pop('is_officeStaff', True),
            'is_deleverystaff': validated_data.pop('is_deleverystaff', False),
            'is_hubadmin': validated_data.pop('is_hubadmin', False),
            'hub': validated_data.pop('hub', None)
        }

        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_staff = True
        user.save()

        staff_data['user'] = user
        Staff.objects.create(**staff_data)

        return user




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields ='__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data) 
        user.set_password(password)
        user.is_staff=True
        user.save()
        return user

class OfficeStaffViewSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model = Staff
        fields = ('id','user','age', 'address', 'joining_date','is_officeStaff','is_deleverystaff','hub','is_hubadmin')
        extra_kwargs = {'password': {'write_only': True}}
class HubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hub
        fields = '__all__'
class DeliveryStaffSerializer(serializers.ModelSerializer):
    user=UserSerializer()
    class Meta:
        model = Staff
        fields = '__all__'
class StaffSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    name = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)
    profile_picture = serializers.ImageField(write_only=True)
    phone = serializers.IntegerField(write_only=True)
    password=serializers.CharField(write_only=True)
    is_active=serializers.BooleanField(write_only=True)
    class Meta:
        model = Staff
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        staff_data={
            'age': validated_data.pop('age', None),
            'address': validated_data.pop('address', None),
            'joining_date': validated_data.pop('joining_date', date.today()),
            'is_officeStaff': validated_data.pop('is_officeStaff', False),
            'is_deleverystaff': validated_data.pop('is_deleverystaff', False),
            'is_hubadmin':validated_data.pop('is_hubadmin', False),
        }
        if self.context['request'].user.is_superuser:
            staff_data['hub']=validated_data.pop('hub')
        else:
            staff_data['hub']=self.context['request'].user.staff.hub
        validated_data["is_staff"]=True
        validated_data["is_active"]=True
        password=validated_data.pop('password')
        user=CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        staff_data["user"]=user 
        staff=Staff.objects.create(**staff_data)
        return staff
    def update(self, instance, validated_data):
        # Validate email uniqueness
        new_email = validated_data.get('email', instance.user.email)
        if CustomUser.objects.exclude(pk=instance.user.pk).filter(email=new_email).exists():
            raise serializers.ValidationError("Email already exists.")

        # Update the user data
        user_data = {
            'name': validated_data.get('name', instance.user.name),
            'phone': validated_data.get('phone', instance.user.phone),
            'email': new_email,
            'is_active':validated_data.get('is_active', instance.user.is_active),
        }
        
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        # Update the staff data
        instance.age = validated_data.get('age', instance.age)
        instance.address = validated_data.get('address', instance.address)
        instance.is_officeStaff = validated_data.get('is_officeStaff', instance.is_officeStaff)
        instance.is_deleverystaff = validated_data.get('is_deleverystaff', instance.is_deleverystaff)
        instance.is_hubadmin = validated_data.get('is_hubadmin', instance.is_hubadmin)

        instance.save()
        return instance
    def validate(self, data):
        is_hubadmin = data.get('is_hubadmin', False)
        is_deleverystaff = data.get('is_deleverystaff', False)
        is_officeStaff = data.get('is_officeStaff', False)

        if is_hubadmin + is_deleverystaff + is_officeStaff > 1:
            raise ValidationError({"message":"A user cannot be both admin and delivery staff or office staff at the same time."})

        return data