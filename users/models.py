
from django.db import models
from sales_logistics.models import PaymentType
from django.contrib.auth.models import AbstractUser

class SiteUser(AbstractUser):
    phone_number = models.CharField(max_length=15,unique=True,default='')
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True,null=True)

    def __str__(self):
        return self.username
    
    USERNAME_FIELD='username'
    REQUIRED_FIELDS = ['first_name', 'last_name','password']
    
class Country(models.Model):
    country_name = models.CharField(max_length=100)

    def __str__(self):
        return self.country_name

    
class Address(models.Model):
    unit_number = models.CharField(max_length=10, blank=True, null=True)
    street_number = models.CharField(max_length=10)
    address_line1 = models.CharField(max_length=255,db_index=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True,db_index=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.address_line1}, {self.city}'

class UserAddress(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE,db_index=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,db_index=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.address.address_line1}'

class UserPaymentMethod(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)
    account_number = models.CharField(max_length=20, unique=True)
    expiry_date = models.DateField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.payment_type}'