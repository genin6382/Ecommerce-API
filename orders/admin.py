from django.contrib import admin
from .models import OrderStatus, ShopOrder, OrderLine, ShoppingCart, ShoppingCartItem
# Register your models here.
admin.site.register(OrderStatus)
admin.site.register(ShopOrder)
admin.site.register(OrderLine)
admin.site.register(ShoppingCart)
admin.site.register(ShoppingCartItem)
