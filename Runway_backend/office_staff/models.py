# from django.contrib.gis.db import models
# from users.models import Users
# from hubs.models import Hub


# # Create your models here.


# class Staff(Users):
#     age = models.PositiveIntegerField()
#     address = models.CharField(max_length=200)
#     joining_date = models.DateField()
#     # is_officeStaff=models.BooleanField(default=False)
#     # is_deleverystaff=models.BooleanField(default=False)
#     hub = models.ForeignKey(Hub, on_delete=models.SET_NULL, null=True, related_name='staff_members')

#     def __str__(self):
#         return self.email