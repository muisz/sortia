from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True, db_index=True)
    picture = models.ImageField(upload_to='users/', null=True, blank=True)

    BUYER = '1'
    SELLER = '2'
    ROLE_CHOICES = (
        (BUYER, 'Buyer'),
        (SELLER, 'Seller'),
    )
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
