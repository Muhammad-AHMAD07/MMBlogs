from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('writer', 'Writer'),
        ('viewer', 'Viewer'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    
    # accounts/models.py
def __str__(self):
    return self.username