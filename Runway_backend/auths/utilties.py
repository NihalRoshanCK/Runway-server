import requests
from rest_framework import permissions
from rest_framework.permissions import BasePermission
import pyotp
from django.core.mail import send_mail

def genarate_otp(email):
    totp = pyotp.TOTP(pyotp.random_base32())
    otp = totp.at(0)

    # Send OTP via email
    send_mail(
        'OTP Verification',
        f'Your OTP is: {otp}',
        'sender@example.com',
        [email],  # Use user.email instead of undefined email variable
        fail_silently=False,
        )
    return otp

class IsHubAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user has a related Staff object
        if hasattr(request.user, 'staff'):
            staff = request.user.staff

            # Check if the staff member is a hub admin
            return staff.is_hubadmin

        return False
class IsOfficeStaff(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is office staff
        return request.user.staff.is_officeStaff

class IsDeleveryStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.staff.is_deleverystaff
class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.staff