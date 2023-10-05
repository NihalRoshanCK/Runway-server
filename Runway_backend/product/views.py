from django.shortcuts import render
from django.db.models import Q
import random,datetime
from rest_framework import viewsets,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser
from product.models import Category,Booking,Payment,Order,Worksheet
from .serializers import CategorySerializer,BookingSerializer,PaymentSerializer,OrderSerializer,WorksheetSerializer
# ,OrderSerializer
from rest_framework import generics,status
from auths.utilties import IsHubAdmin, IsOfficeStaff,IsDeleveryStaff,IsStaff
from django.db.models.functions import TruncMonth
from  product.tasks import asign_route
from django.db.models import Count, F
from datetime import timedelta
import datetime
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    


class BookingViewSet(viewsets.ModelViewSet):
    queryset=Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes=[permissions.IsAuthenticated]
    
class PaymentViewSet(viewsets.ModelViewSet):
    queryset=Payment.objects.all()
    serializer_class = PaymentSerializer
    pagination_class=[permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)

        if serializer.is_valid():
            response_data = serializer.save()
            asign_route.delay(response_data['order'])
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    
    
    def get_permissions(self):
        if self.action in ['partial_update', 'retrieve', 'list']:
            return [IsAuthenticated()]  
        elif self.action == 'create':
            return [AllowAny()]
        elif self.action == 'reset_asign_flag':
            return [AllowAny()]
        elif self.action in ['pending_oders','order_asign']:
            return [IsOfficeStaff()]
        else:
            return [IsAdminUser() or IsHubAdmin()]

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser:
            # Superusers can see all orders
            queryset = self.get_queryset()
        elif  request.user.staff.is_hubadmin or request.user.staff.is_officeStaff:
            queryset = self.get_queryset().filter(current_position=request.user.staff.hub)
        else:
            # Regular users can only see their own orders
            queryset = Order.objects.filter(booking__user=request.user)
            # queryset=Booking.objects.f
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the current user is the owner of the instance or an admin
        if instance.booking.user == request.user or request.user.is_superuser or request.user.staff.is_officeStaff or request.user.staff.is_deleverystaff:
            return super().partial_update(request, *args, **kwargs)
        else:
            raise ValidationError("You are not allowed to update this order.")
    @action(detail=False, methods=['GET'])
    def pending_oders(self, request):
        if request.user._is_superuser:
            queryset=Order.objects.filter(status='pending')
        else:   
            queryset=Order.objects.filter(booking__from_hub=request.user.staff.hub,status='pending')
            
    
    @action(detail=False, methods=['POST'])
    def order_asign(self, request):
        try:
            order_id = request.data.get('orderId')
            order = Order.objects.get(order_id=order_id, asign=False)
            
            # You should pass the 'order' instance to the serializer, not 'queryset'
            serializer = self.get_serializer(order)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or already assigned"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['GET'])
    def pending_order(self, request):
        if request.user.is_superuser:
            queryset = self.get_queryset().filter(collected=False)
        elif request.user.staff.is_officeStaff or request.user.staff.is_hubadmin:
            queryset = self.get_queryset().filter(booking__from_hub=request.user.staff.hub,collected=False,asign=False) 
        else:
            raise ValidationError("You are not allowed to update this order.")
            return Response (status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(detail=False, methods=['PATCH'])
    def reset_asign_flag(self, request):
        try:
            # Find all orders with asign=True and set asign=False
            orders_to_reset = Order.objects.filter(asign=True)
            orders_to_reset.update(asign=False)

            return Response({"message": "Asign flag reset for all orders"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['GET'])
    def orders_by_month(self, request):
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
        sorted_results = dict(sorted(results.items()))

        return Response(sorted_results)

    def get_month_range(self):
        current_month = datetime.now()
        for i in range(12):
            yield current_month
            current_month -= timedelta(days=current_month.day)
    
class WorksheetViewSet(viewsets.ModelViewSet):
    queryset = Worksheet.objects.all()
    serializer_class = WorksheetSerializer  # Create a serializer for Worksheet model
    
    # Override the create method
    def create(self, request, *args, **kwargs):
        # Assuming you send a list of order IDs in the request data
        order_ids = request.data.get('orders', [])
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        rand = str(random.randint(1111111,9999999))
        sheet_number = current_date + rand
        sheet_number = 'Sheet'+ sheet_number
        request.data["name"]=sheet_number
        # Create the worksheet
        worksheet_serializer = self.get_serializer(data=request.data)
        if worksheet_serializer.is_valid():
            worksheet = worksheet_serializer.save()

            # Mark all associated orders as asign=True
            orders_to_update = Order.objects.filter(id__in=order_ids)
            orders_to_update.update(asign=True)

            return Response(worksheet_serializer.data, status=status.HTTP_201_CREATED)
        return Response(worksheet_serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
    def partial_update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Iterate through the orders in the worksheet
        for order in instance.orders.all():
            if not order.collected and order.status == 'in_progress' :
                order.collected = True
            order.asign = False
            order.save()
        self.perform_update(serializer)

        return Response(serializer.data)
    @action(detail=False, methods=['GET'])
    def get_self_worksheet(self, request):
        queryset = self.get_queryset().filter(user=request.user.staff,is_closed=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)