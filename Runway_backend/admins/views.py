from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,serializers
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView, ListAPIView,ListCreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from users.serializers import UserSerializer
from admins.serializers import HubSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from hubs.models import Hub
from auths.models import Staff,CustomUser
from rest_framework import viewsets,permissions  
from admins.serializers import HubSerializer,HubAdminSerializer,HubAdminViewSetSerialize,HubCreationSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser,BasePermission
from product.models import Payment,Order
from auths.utilties import IsHubAdmin


from django.db.models.functions import TruncMonth
# Create your views here.


# class IsHubAdmin(BasePermission):
#     def has_permission(self, request, view):
#         return request.user.staff.is_hubadmin

# class HubViewSet(viewsets.ModelViewSet):
#     queryset = Hub.objects.all()
#     serializer_class = HubSerializer
#     permission_classes = [IsAuthenticated | IsAdminUser ]    

class HubAdminRegistrationView(CreateAPIView):
    permission_classes = [IsAuthenticated & (IsAdminUser | IsHubAdmin)]
    serializer_class = HubAdminSerializer
    
    def perform_create(self, serializer):
        serializer.save()
        
class HubAdminViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class=HubAdminViewSetSerialize
    
# class HubViewSet(viewsets.ModelViewSet):
#     queryset = Hub.objects.all()
#     serializer_class = HubSerializer
#     permission_classes = [IsAdminUser]
    
    # def create(self, request, *args, **kwargs):
        # Extract hub data from request
    
class HubViewSet(viewsets.ModelViewSet):
    queryset = Hub.objects.all()
    serializer_class = HubCreationSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except serializers.ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
    
class AdminDash(APIView):
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
            created_at__gte=current_month_start, created_at__lte=current_month_end
        ).count()

        # Count the number of orders for the previous month
        prev_month_orders = Order.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end
        ).count()

        # Calculate the difference between current and previous month orders
        orders_difference = current_month_orders - prev_month_orders

        # Get the total number of orders
        total_orders = Order.objects.all().count()

        # Getting User details
        # Count the number of Users for the current month
        current_month_users = CustomUser.objects.filter(
            created_at__gte=current_month_start, created_at__lte=current_month_end
        ).count()

        # Count the number of staff for the current month
        current_month_staff = Staff.objects.filter(
            created_at__gte=current_month_start, created_at__lte=current_month_end
        ).count()

        # Count the number of users for the previous month
        prev_month_users = CustomUser.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end
        ).count()

        # Count the number of staff for the previous month
        prev_month_staff = Staff.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end
        ).count()

        # Calculate the difference between current and previous month users and staff
        user_difference = current_month_users - prev_month_users
        staff_difference = current_month_staff - prev_month_staff

        # Calculate the difference between current and previous month users (excluding staff)
        current_month_user = current_month_users - current_month_staff
        prev_month_user = prev_month_users - prev_month_staff

        # Calculate the exact number of users
        exact_users = user_difference - staff_difference

        # Get the total number of Users and Staff
        total_users = CustomUser.objects.all().count()
        total_staff = Staff.objects.all().count()

        # Calculate the exact total of users
        exact_total_users = total_users - total_staff

        # Check if prev_month_user is zero before division
        if prev_month_user != 0:
            users_difference = ((current_month_user - prev_month_user) / prev_month_user) * 100
        else:
            users_difference = current_month_user - prev_month_user * 100  # If no previous month users, use current month count as 100%

        # Getting hub details
        # Count the number of hubs for the current month
        current_month_hubs = Hub.objects.filter(
            created_at__gte=current_month_start, created_at__lte=current_month_end
        ).count()

        # Count the number of hubs for the previous month
        prev_month_hubs = Hub.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end
        ).count()

        # Get the total number of hubs
        total_hubs = Hub.objects.all().count()

        # Check if prev_month_hubs is zero before division
        if prev_month_hubs != 0:
            hub_difference = ((current_month_hubs - prev_month_hubs) / prev_month_hubs) * 100
        else:
            hub_difference = current_month_hubs * 100  # If no previous month hubs, use current month count as 100%

        # Count the number of payments for the current month
        current_month_payment = Payment.objects.filter(
            created_at__gte=current_month_start, created_at__lte=current_month_end
        )

        # Count the number of payments for the previous month
        prev_month_payment = Payment.objects.filter(
            created_at__gte=prev_month_start, created_at__lte=prev_month_end
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
            
        # Define the possible statuses
        possible_statuses = ['pending', 'in_progress', 'completed', 'return']
        
        # Get the order counts grouped by month and status
        queryset = (
            Order.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month', 'status')
            .annotate(order_count=Count('id'))
            .order_by('month', 'status')
        )

        # Create a dictionary to store the results
        results = {}
        for month in self.get_month_range():
            month_str = month.strftime('%Y-%m')
            results[month_str] = {status: 0 for status in possible_statuses}

        for item in queryset:
            month = item['month'].strftime('%Y-%m')
            status = item['status']
            order_count = item['order_count']
            results[month][status] = order_count

        # Sort the results by month
        order_month_data = dict(sorted(results.items()))
        data = {
            "orders": {
                "total": total_orders,
                "current_month": current_month_orders,
                "prev_month": prev_month_orders,
                "difference": orders_difference,
                'order_month_data':order_month_data
            },
            'users': {
                "total": exact_total_users,
                "current_month": current_month_users,
                "prev_month": prev_month_users,
                "difference": users_difference
            },
            'hubs': {
                "total": total_hubs,
                "current_month": current_month_hubs,
                "prev_month": prev_month_hubs,
                "difference": hub_difference
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