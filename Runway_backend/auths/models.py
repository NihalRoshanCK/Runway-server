from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.gis.db import models
# from hubs.models import Hub

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) # Password hashing is done here
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_picture/', null=True)
    name=models.CharField(max_length=150)
    phone=models.BigIntegerField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Staff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff')
    age = models.PositiveIntegerField()
    address = models.CharField(max_length=200)
    joining_date = models.DateField(null=True)
    is_officeStaff = models.BooleanField(default=False)
    is_deleverystaff = models.BooleanField(default=False)
    is_hubadmin=models.BooleanField(default=False)
    hub = models.ForeignKey('hubs.Hub', on_delete=models.SET_NULL, null=True, related_name='staff_members')

    def __str__(self):
        return self.user.email
    
    # def get_chat_messages(self):
    #     return ChatMessage.objects.filter(hub=self.hub)