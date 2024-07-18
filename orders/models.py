from django.db import models

class OrderStatus(models.Model):
    status = models.CharField(max_length=50,db_index=True)
    message=models.TextField(null=True,blank=True)
    def __str__(self):
        return self.status

class ShopOrder(models.Model):
    user = models.ForeignKey('users.SiteUser', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.ForeignKey('users.UserPaymentMethod', on_delete=models.CASCADE,db_index=True)
    shipping_address = models.ForeignKey('users.Address', on_delete=models.CASCADE,db_index=True)
    shipping_method = models.ForeignKey('sales_logistics.ShippingMethod', on_delete=models.CASCADE)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)

    def __str__(self):
        return f'Order {self.id} ({self.user.username} - {self.order_date}): Total ${self.order_total}'


class OrderLine(models.Model):
    order = models.ForeignKey(ShopOrder, on_delete=models.CASCADE)
    product_item = models.ForeignKey('products.ProductItem', on_delete=models.CASCADE,db_index=True)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return f'{self.order} - {self.qty} x {self.product_item.name} (${self.price} each)'


class ShoppingCart(models.Model):
    user = models.ForeignKey('users.SiteUser', on_delete=models.CASCADE)

    def __str__(self, *args, **kwargs):
        return self.user.username

class ShoppingCartItem(models.Model):
    cart = models.ForeignKey(ShoppingCart, on_delete=models.CASCADE,db_index=True)
    product_item = models.ForeignKey('products.ProductItem', on_delete=models.CASCADE,db_index=True)
    qty = models.IntegerField()

    def __str__(self):
        return f' {self.cart} - {self.product_item.name} ' 

