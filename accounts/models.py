from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'Donor'),
        ('seeker', 'Blood Seeker'),
        ('hospital', 'Hospital'),
        ('blood_bank', 'Blood Bank'),
        ('college', 'College'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )
# Create your models here.
