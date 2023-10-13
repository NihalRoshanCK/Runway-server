from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser,BasePermission
from auths.models import Staff
from hubs.serializer import OfficeStaffSerializer,DeliveryStaffSerializer,UserSerializer,OfficeStaffViewSerializer,HubSerializer,StaffSerializer
from rest_framework import viewsets
from geopy.geocoders import Nominatim
from rest_framework.generics import CreateAPIView
from datetime import timedelta
from geopy.distance import great_circle
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from rest_framework.views import APIView
from hubs.models import Hub
import requests
from auths.utilties import IsHubAdmin,IsOfficeStaff,IsDeleveryStaff
from datetime import datetime, timedelta
from django.utils import timezone

from product.models import Order,Payment
# Create your views here.

# class IsHubAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.staff.is_hubadmin
# class IsOfficeStaff(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.staff.is_officeStaff

# class IsDeleveryStaff(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.staff.is_deleverystaff
# class IsStaff(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.staff
# class OfficeStaffRegistrationView(CreateAPIView):
#     permission_classes = [IsAuthenticated & (IsAdminUser | IsHubAdmin)]
#     def post(self, request, *args, **kwargs):
#         userserializer=UserSerializer(data=request.data)
#         userserializer.is_valid(raise_exception=True)
#         user=userserializer.save()
#         request.data['user']=user.id
#         serializer = OfficeStaffSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfficeStaffRegistrationView(CreateAPIView):
    serializer_class = OfficeStaffSerializer
    permission_classes = [IsAdminUser or IsHubAdmin]
    
    def perform_create(self, serializer):
        serializer.save()
        
        
class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class=StaffSerializer
    permission_classes=[ IsAdminUser or IsHubAdmin]
    
    
class DeliveryStaffRegistrationView(CreateAPIView):
    permission_classes = [IsAdminUser or IsHubAdmin]
    serializer_class = DeliveryStaffSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        
class OfficeUserViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = OfficeStaffViewSerializer
    permission_classes = [IsAdminUser or IsHubAdmin]
    

class DeliveryStaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.filter(is_deleverystaff=True)
    serializer_class = DeliveryStaffSerializer
    
    def get_permissions(self):
        if self.action == ['partial_update','create']:
            return [IsAdminUser() or IsHubAdmin()]
        elif self.action == 'retrieve':
            return [IsAdminUser() or IsHubAdmin() or IsOfficeStaff()]
        elif self.action == 'list':
            return [IsAuthenticated()]
        
    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            queryset = self.get_queryset()
        elif  request.user.staff.is_hubadmin or request.user.staff.is_officeStaff:
            queryset = self.get_queryset().filter(hub=request.user.staff.hub)
        else:
            raise ValidationError("You are not allowd this point")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    


class HubDistanceView(APIView):
    def post(self, request, *args, **kwargs):
        from_zipcode = request.data.get('from_zipcode')
        to_zipcode = request.data.get('to_zipcode')
        #url for calling api for get cordinates using zip code
        zip_api_url = "https://api.mapbox.com/geocoding/v5/mapbox.places/{place_id}.json"
        
        #url for getting distance between hub and location using cordinates
        distance_api_url = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{coordinates}"
        
        
        #access key for mapbox
        access_token = "pk.eyJ1IjoibmloYWxyb3NoYW4iLCJhIjoiY2xsZGIyNW5wMGFxMjN1cXkwZm5reHlrdSJ9.l2JGuFbgbkgYWJl4vDOUig"
        
        # params for api call url
        params = {
        "access_token": access_token,
        }
        #setting the format of calling  distance api 
        from_api_url = zip_api_url.format(place_id=from_zipcode) #from address url format
        to_api_url = zip_api_url.format(place_id=to_zipcode) #to address url format
        
        # getting response from the api
        from_response = requests.get(from_api_url, params=params)
        to_response = requests.get(to_api_url, params=params)
        try:
            #getting data from the response
            if from_response.status_code == 200:
                data = from_response.json()
                
                if len(data['features']) > 0:
                    from_cordinates=data['features'][0]['center']
                    from_longitude=from_cordinates[0]
                    from_latitude=from_cordinates[1]
            if to_response.status_code == 200:
                data = to_response.json()
                
                if len(data['features']) > 0:
                    to_cordinates=data['features'][0]['center']
                    to_longitude=to_cordinates[0]
                    to_latitude=to_cordinates[1]
            
        # Chekking all the data is geting 
        except:
            return Response({"error": "Invalid zipcodes provided." ,"on":"on gettinglongitude and latitude from zipcode "}, status=400)
        hubs = Hub.objects.all()
        
        # Find nearby hubs within 20 km of each point
       
        nearby_from_hub= [{"distance": 20000 ,"hub_name":None}]
        nearby_to_hub = [{"distance": 20000 ,"hub_name":None}]
        
        try:
            # iterating all the Hubs
            for hub in hubs:
                # calling api to checking the distance between the from_zipcode and hub 
                from_coordinates_str = f"{from_longitude},{from_latitude};{hub.location.x},{hub.location.y}"
                from_distance_api_url = distance_api_url.format(coordinates=from_coordinates_str)
                from_distance_response = requests.get(from_distance_api_url, params=params)
                
                # calling api to checking the distance between the to_zipcode and hub 
                to_coordinates_str = f"{to_longitude},{to_latitude};{hub.location.x},{hub.location.y}"
                to_distance_api_url = distance_api_url.format(coordinates=to_coordinates_str)
                to_distance_response = requests.get(to_distance_api_url, params=params)
                
                # getting the response from the api 
                if from_distance_response.status_code == 200:
                    data = from_distance_response.json()
                    if len(data['routes']) > 0:
                        from_hub_distance = data['routes'][0]['distance']
                        if from_hub_distance <50000 and from_hub_distance < nearby_from_hub[0]["distance"] :
                            nearby_from_hub= []
                            nearby_from_hub.append({"hub_name": hub.hub_name, "distance": from_hub_distance,"hub.location.x":hub.location.x,"hub.location.y":hub.location.y})
                
                # getting the response from the api 
                if to_distance_response.status_code == 200:
                    data = to_distance_response.json()
                    if len(data['routes']) > 0:
                        to_hub_distance = data['routes'][0]['distance']
                        if to_hub_distance <50000 and to_hub_distance < nearby_to_hub[0]["distance"]:
                            nearby_to_hub = []
                            nearby_to_hub.append({"hub_name": hub.hub_name, "distance": to_hub_distance,"hub.location.x":hub.location.x,"hub.location.y":hub.location.y})
        except:
            return Response({" message": "service not availabl ","on":"on iteration"}, status=400)
        try:
            if nearby_from_hub[0]['distance'] and nearby_to_hub[0]['distance']:
                from_to_hub_coordinates_str = f"{from_longitude},{from_latitude};{nearby_from_hub[0]['hub.location.x']},{nearby_from_hub[0]['hub.location.y']}"
                to_to_hub_coordinates_str = f"{to_longitude},{to_latitude};{nearby_to_hub[0]['hub.location.x']},{nearby_to_hub[0]['hub.location.y']}"
                hub_to_hub_coordinates_str = f"{nearby_from_hub[0]['hub.location.x']},{nearby_from_hub[0]['hub.location.y']};{nearby_to_hub[0]['hub.location.x']},{nearby_to_hub[0]['hub.location.y']}"
                
                from_to_hub_distance_api_url = distance_api_url.format(coordinates=from_to_hub_coordinates_str)
                to_to_hub_distance_api_url = distance_api_url.format(coordinates=to_to_hub_coordinates_str)
                hub_to_hub_distance_api_url = distance_api_url.format(coordinates=hub_to_hub_coordinates_str)
                
                from_to_hub_distance_response = requests.get(from_to_hub_distance_api_url, params=params)
                to_to_hub_distance_response = requests.get(to_to_hub_distance_api_url, params=params)
                hub_to_hub_distance_response = requests.get(hub_to_hub_distance_api_url, params=params)
                
                if from_to_hub_distance_response.status_code == 200:
                    from_to_hub_distance_data = from_to_hub_distance_response.json()
                    if len(from_to_hub_distance_data['routes']) > 0:
                        from_to_hub_distance = from_to_hub_distance_data['routes'][0]['distance']
                        
                if to_to_hub_distance_response.status_code == 200:
                    to_to_hub_distance_data = to_to_hub_distance_response.json()
                    if len(to_to_hub_distance_data['routes']) > 0:
                        to_to_hub_distance = to_to_hub_distance_data['routes'][0]['distance']
                
                if hub_to_hub_distance_response.status_code == 200:
                    hub_to_hub_distance_data = hub_to_hub_distance_response.json()
                    if len(hub_to_hub_distance_data['routes']) > 0:
                        hub_to_hub_distance = hub_to_hub_distance_data['routes'][0]['distance']   
                if (from_to_hub_distance and to_to_hub_distance and hub_to_hub_distance) is not None:
                    distance=from_to_hub_distance+to_to_hub_distance+hub_to_hub_distance
                
                try:
                    if distance <= 40000:
                        time_period='1day'
                    elif distance <= 120000:
                        time_period='2day'
                    else:
                        time_period='3day'
                except:
                    pass
            
            data = {
            'time_period':time_period,
            'nearby_hubs_from':nearby_from_hub,
            'nearby_hubs_to':nearby_to_hub
            }
        except:
            return Response({" message: service not available "}, status=400)
            
        
        return Response(data, status=200)


class HubDash(APIView):
    def get(self, request, *args, **kwargs):
        # Calculate the current month's start and end dates
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = (current_month_start + timedelta(days=32)).replace(day=1)
        current_month_end = next_month_start - timedelta(days=1)

        # Calculate the previous month's start and end dates
        prev_month_end = current_month_start - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        # Count the number of orders for the current month
        current_month_orders = Order.objects.filter(
            created_at__gte=current_month_start, created_at__lte=current_month_end,booking__to_address=request.user.staff.hub
        ).count()

        # Count the number of orders for the previous month
        prev_month_orders = Order.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end,booking__to_address=request.user.staff.hub
        ).count()

        # Calculate the difference between current and previous month orders
        orders_difference = current_month_orders - prev_month_orders

        # Get the total number of orders
        total_orders = Order.objects.filter(booking__to_address=request.user.staff.hub).count()

        
        
        # Count the number of staff for the current month
        current_month_staff = Staff.objects.filter(
            created_at__gte=current_month_start, created_at__lte=current_month_end
        ).count()
        
        
        # Count the number of staff for the previous month
        prev_month_staff = Staff.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end ,hub=request.user.staff.hub
        ).count()

        total_staff = Staff.objects.filter(hub=request.user.staff.hub).count()

       

        # Check if prev_month_user is zero before division
        if prev_month_staff != 0:
            staff_difference = ((current_month_staff - prev_month_staff) / prev_month_staff) * 100
        else:
            staff_difference = current_month_staff - prev_month_staff * 100  # If no previous month users, use current month count as 100%

        
        # Count the number of payments for the current month
        current_month_payment = Payment.objects.filter(
            created_at__gte=current_month_start, created_at__lte=current_month_end,order__booking__to_hub=request.user.staff.hub
        )

        # Count the number of payments for the previous month
        prev_month_payment = Payment.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end,order__booking__to_hub=request.user.staff.hub
        )

        current_month_amount = 0
        # Calculate the amount of payments in the current month
        for payment in current_month_payment:
            current_month_amount += payment.amount

        prev_month_amount = 0
        # Calculate the amount of payments in the previous month
        for payment in prev_month_payment:
            prev_month_amount += payment.amount

        # Get the total number of payments
        total_payment = Payment.objects.all()

        total_amount = 0
        for payment in total_payment:
            total_amount += payment.amount

        # Check if prev_month_amount is zero before division
        if prev_month_amount != 0:
            amount_difference = ((current_month_amount - prev_month_amount) / prev_month_amount) * 100
        else:
            amount_difference = current_month_amount-prev_month_amount * 100  # If no previous month amount, use current month amount as 100%
            
        
        data = {
            "orders": {
                "total": total_orders,
                "current_month": current_month_orders,
                "prev_month": prev_month_orders,
                "difference": orders_difference,
                # 'order_month_data':order_month_data
            },
            'Staff': {
                "total": total_staff,
                # "current_month": current_month_users,
                "prev_month": prev_month_staff,
                "difference": staff_difference
            },
            'payment': {
                "total": total_amount,
                "current_month": current_month_amount,
                "prev_month": prev_month_amount,
                "difference": amount_difference
            }
        }

        return Response(data)
    def get_month_range(self):
        current_month = datetime.now()
        for i in range(12):
            yield current_month
            current_month -= timedelta(days=current_month.day)