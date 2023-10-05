from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
import requests
from auths.serializer import UserSerializer
from product.models import Category,Order,Booking,Payment,Worksheet
from hubs.models import Hub

import random,datetime

from product.utilities import find_nearby_hubs,geocode_location

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model=Booking
        fields="__all__"
    
    def create(self, validated_data):
        from_location = validated_data.get('from_address')
        to_location = validated_data.get('to_address')
        # Perform geocoding for 'from_location'
        from_cordinates = geocode_location(from_location)
        if not from_cordinates:
            raise ValidationError({"message": "Geocoding error for 'from_address'"})

        # Perform geocoding for 'to_location'
        to_cordinates = geocode_location(to_location)
        if not to_cordinates:
            raise ValidationError({"message": "Geocoding error for 'to_address'"})

        # Find nearby hubs
        nearby_from_hubs =find_nearby_hubs(from_cordinates)
        nearby_to_hubs =  find_nearby_hubs(to_cordinates)
        
        if not nearby_from_hubs :
            raise ValidationError({"message": "No nearby hubs found from hub"})

        if not nearby_to_hubs:
            raise ValidationError({"message": "No nearby hubs found to hub"})

        # Set the closest hubs for 'from_hub' and 'to_hub' fields
        validated_data['from_hub'] = nearby_from_hubs[0]['hub']
        validated_data['category']=Category.objects.get(id=validated_data['category'].id)
        validated_data['to_hub'] = nearby_to_hubs[0]['hub']
        validated_data['user']=self.context['request'].user
        booking = Booking(**validated_data)
        booking.save()
        return booking

class OrderSerializer(serializers.ModelSerializer):
    booking=BookingSerializer(read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
    
   
        
class PaymentSerializer(serializers.ModelSerializer):
    booking = serializers.IntegerField(write_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = Payment
        fields = ('booking', 'amount', 'payment_id', 'method',)
        
    def create(self, validated_data):
        
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        rand = str(random.randint(1111111,9999999))
        order_number = current_date + rand
        order_number = 'Runway'+ order_number
        
        order_data = {
            'order_id': order_number,
            'booking': Booking.objects.get(pk=validated_data['booking']),
            'status': 'pending'
        }
        order_data['current_position']=order_data['booking'].from_hub
        order = Order.objects.create(**order_data)
        
        payment_data = {
            'amount':validated_data['amount'],
            'payment_id': validated_data['payment_id'],
            'method': validated_data['method'],
            'order': order  # Link the payment to the created order
        }
        
        payment = Payment.objects.create(**payment_data)
        response_data = {
            'Booking':BookingSerializer(order_data['booking']).data,
            'payment': PaymentSerializer(payment).data,
            'order': OrderSerializer(order).data,  # Assuming you have an OrderSerializer
        }
        
        return response_data
    
class WorksheetSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(read_only=True ,many=True)
    class Meta:
        model = Worksheet
        fields = '__all__'