from rest_framework import serializers
from auths.models import Staff,CustomUser
from hubs.models import Hub
from datetime import date


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
        model = Staff
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
            'is_hubadmin':validated_data.pop('is_hubadmin', None)
        }
        if self.context['request'].user.is_superuser:
            staff_data['hub']=validated_data.pop('hub')
        else:
            staff_data['hub']=self.context['request'].user.staff.hub
        validated_data["is_staff"]=True
        password=validated_data.pop('password')
        user=CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        staff_data["user"]=user 
        staff=Staff.objects.create(**staff_data)
        return staff