from django.contrib.gis.db import models
from hubs.models import Hub
from django.contrib.postgres.fields import JSONField
from auths.models import CustomUser,Staff
from socketSystem.models import Notification,NotificationContent
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    price=models.IntegerField()

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    product_name=models.CharField(max_length=200)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    verification= models.JSONField(null=True)  # You can use JSONField to store verification data as a dictionary.
    from_address= models.CharField(max_length=200)
    to_address=models.CharField(max_length=200)
    from_zipcode=models.CharField(max_length=6)
    to_zipcode=models.CharField(max_length=6)
    product_price=models.BigIntegerField()
    from_user_contact=models.BigIntegerField()
    to_user_contact=models.BigIntegerField()
    hbd=models.DateField()
    cpd=models.DateField()
    weight=models.DecimalField(max_digits=6, decimal_places=2)
    height=models.DecimalField(max_digits=6, decimal_places=2)
    width=models.DecimalField(max_digits=6, decimal_places=2)
    from_hub=models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True, related_name='orders_from')
    to_hub=models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True, related_name='orders_to')
    created_at = models.DateTimeField(auto_now_add=True)

    
    
    def __str__(self):
        return f"Booking: {self.product_name} (Created at: {self.created_at})"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('return', 'Return'),
    ]
    order_id=models.CharField(max_length=100, unique=True)
    booking=models.OneToOneField(Booking, on_delete=models.CASCADE, null=True, blank=True)
    current_position=models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True)
    asign=models.BooleanField(default=False)
    collected=models.BooleanField(default=False)
    route_added=models.BooleanField(default=False)
    status=models.CharField(max_length=50, choices=STATUS_CHOICES)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        if not self.pk:
            message=f"{'A new booking as been created on order id :'}{self.order_id}"
            notification_condent=NotificationContent.objects.create(message=message)
            notification=Notification.objects.create(user=self.booking.from_hub.hub_head,content=notification_condent)
            print(notification)
        super(Order, self).save(*args, **kwargs)

PAYMENT_METHOD_CHOICES = [
    ('credit_card', 'Credit Card'),
    ('razorpay', 'RazorPay'),
    ('bank_transfer', 'Bank Transfer'),
]
class Payment(models.Model):
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    payment_id=models.CharField(max_length=100, unique=True)
    method=models.CharField(max_length=50,choices=PAYMENT_METHOD_CHOICES)
    order=models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Payment: {self.amount} (Method: {self.method})'

class Route(models.Model):
    route= models.JSONField(null=True)
    order=models.OneToOneField(Order, on_delete=models.SET_NULL, null=True)
    is_routed=models.BooleanField(default=False)

class Worksheet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    orders = models.ManyToManyField(Order)
    user=models.ForeignKey(Staff,on_delete=models.CASCADE)
    is_closed=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
