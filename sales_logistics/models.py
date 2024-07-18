from django.db import models
from products.models import ProductCategory  

class PaymentType(models.Model):
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.value

class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Promotion(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class PromotionCategory(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE)

    def __str__(self):
        return self.category.category_name + ' - ' + self.promotion.name
