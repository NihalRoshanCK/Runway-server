from rest_framework.serializers import ModelSerializer
from rest_framework import serializers,status
from hubs.models import Hub
from auths.models import CustomUser,Staff
from auths.serializer import UserSerializer
from django.contrib.gis.geos import Point
from datetime import datetime
from pytz import timezone
from django.db import IntegrityError,transaction
from rest_framework.response import Response
from datetime import date
class UserStaffSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        
class StaffSerializer(ModelSerializer):
    user = UserStaffSerializer()
    class Meta:
        model = Staff
        fields = '__all__'
        
class HubSerializer(ModelSerializer):
    hub_head = StaffSerializer(source='hub_head.staff')
    staffs = serializers.SerializerMethodField()  # Custom method field for staffs
    
    def get_staffs(self, obj):
        # Retrieve all staff details having the same hub as the current hub object (obj)
        staffs_same_hub = Staff.objects.filter(hub=obj,is_hubadmin=False)
        return StaffSerializer(staffs_same_hub, many=True).data

    class Meta:
        model = Hub
        fields = '__all__'

class HubAdminViewSetSerialize(ModelSerializer):
    hub = HubSerializer()
    user = UserStaffSerializer()
    class Meta:
        model = Staff
        fields = '__all__'
        
class HubAdminSerializer(serializers.ModelSerializer):
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
            'is_deleverystaff': validated_data.pop('is_deleverystaff', True),
            'is_hubadmin': validated_data.pop('is_hubadmin', True),
            'hub': validated_data.pop('hub', None)
        }

        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_staff = True
        user.save()

        staff_data['user'] = user.id
        Staff.objects.create(**staff_data)
        return user

class HubCreationSerializer(serializers.ModelSerializer):
    # Extract hub data from request
    age = serializers.IntegerField(write_only=True)
    address = serializers.CharField(write_only=True)
    email = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    phone = serializers.IntegerField(write_only=True)
    admin_address = serializers.CharField(write_only=True)
    hub_head = StaffSerializer(source='hub_head.staff', read_only=True)  # Serialize hub_head with StaffSerializer
    staffs = serializers.SerializerMethodField()  # Custom method field for staffs
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Hub
        fields = '__all__'
    
    def get_staffs(self, obj):
        # Retrieve all staff details having the same hub as the current hub object (obj)
        staffs_same_hub = Staff.objects.filter(hub=obj)
        return StaffSerializer(staffs_same_hub, many=True).data

    def create(self, validated_data):
        # Getting the location that we want to convert it into a pointer field in PostGIS
        password = validated_data.pop('password')
        location = validated_data.pop('location', None)
        
        # Collecting the hub_admin data to create hub_admin
        Hub_admin_data = {
            'age': validated_data.pop('age', None),
            'address': validated_data.pop('admin_address', None),
            'joining_date': validated_data.pop('joining_date', date.today()),
            'is_hubadmin': validated_data.pop('is_hubadmin', True),
            'hub': validated_data.pop('hub', None)
        }
        
        # Collecting the user data to create a user
        user_data = {
            'email': validated_data.pop('email', None),
            'name': validated_data.pop('name', None),
            'phone': validated_data.pop('phone', None),
            'is_active': validated_data.pop('is_active', True),
            'is_staff': validated_data.pop('is_staff', True),
        }
        
        try:
            user = CustomUser(**user_data)
            user.set_password(password)
            user.save()
        except IntegrityError as e:
            raise serializers.ValidationError({"message": "User with same email address already exists."})
        
        latitude = location['latitude']
        longitude = location['longitude']
        validated_data['location'] = Point(latitude, longitude, srid=4326)
        try:
            with transaction.atomic():
                hub = Hub.objects.create(**validated_data)
                hub.save()
        except IntegrityError as e:
            user.delete()
            raise serializers.ValidationError({"message": "A hub with the same location already exists."})
            
        Hub_admin_data['hub'] = hub
        Hub_admin_data['user'] = user
        Hubhead = Staff.objects.create(**Hub_admin_data)
        hub.hub_head = user
        hub.save()

        return hub
