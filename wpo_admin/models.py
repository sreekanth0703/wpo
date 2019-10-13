from django.db import models

# Create your models here.

class Employee(models.Model):
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=10)
    dob = models.DateField(null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    updation_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Employee'
        unique_together = (('name', 'email'),)
        index_together = (('name', 'email'),)
