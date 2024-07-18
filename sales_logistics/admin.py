from django.contrib import admin
from .models import PaymentType,ShippingMethod,Promotion,PromotionCategory

# Register your models here.

admin.site.register(PaymentType)
admin.site.register(ShippingMethod)
admin.site.register(Promotion)
admin.site.register(PromotionCategory)
