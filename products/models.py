from django.db import models
import uuid

class ProductCategory(models.Model):
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    category_name = models.CharField(max_length=100)
    image=models.ImageField(upload_to='category_images/', blank=True, null=True, default='category_images/default.jpg')

    def __str__(self):
        return self.category_name
    
class ProductItem(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,default='')
    name = models.CharField(max_length=255, default='')
    description = models.TextField(default='')
    SKU = models.CharField(max_length=100, unique=True)
    qty_in_stock = models.IntegerField()
    product_image = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller=models.CharField(max_length=100, default='')
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name}'
    
    def save(self, *args, **kwargs):
        if not self.SKU:   #only generate sku if its not already set, this prevents from setting sku on every save of the object
            unique_id = str(uuid.uuid4()).replace("-", "")[6:12]
            self.SKU = f"{self.name[:3].upper()}-{unique_id}"
        super().save(*args, **kwargs)

class Variation(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class VariationOption(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.value}'

class ProductConfiguration(models.Model):
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    variation_option = models.ForeignKey(VariationOption, on_delete=models.CASCADE)
    qty_in_stock = models.IntegerField(default=0)
    out_of_stock = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.out_of_stock= self.qty_in_stock <= 0
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f'{self.product_item} : {self.variation_option}'

class Review(models.Model):
    RATING_CHOICES=[
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5')
    ]
    
    user = models.ForeignKey('users.SiteUser', on_delete=models.CASCADE)
    ordered_product = models.ForeignKey('orders.OrderLine', on_delete=models.CASCADE)
    rating_value = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()

    def __str__(self):
        return f'{self.user} - {self.ordered_product.product_item.name} - {self.rating_value} Rating'