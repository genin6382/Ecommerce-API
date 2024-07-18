from rest_framework import serializers
from .models import OrderStatus, ShopOrder, OrderLine, ShoppingCart, ShoppingCartItem
from products.models import ProductItem
from django.db import transaction
from django.db.models import F
from products.models import ProductItem
from users.models import Address
from sales_logistics.serializers import  ShippingMethodSerializer 
from sales_logistics.models import PromotionCategory, Promotion
from django.utils import timezone
class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductItem
        fields=['id','name','product_image','price']

class ShoppingCartItemSerializer(serializers.ModelSerializer):
    cart_owner=serializers.SerializerMethodField()
    product_details=ProductItemSerializer(source='product_item',read_only=True)
    class Meta:
        model = ShoppingCartItem
        fields = ['id', 'cart','cart_owner','product_item','product_details','qty']

        extra_kwargs={
            'qty':{'allow_null':False,'min_value':1},
            'product_item':{'allow_null':False,'write_only':True},
            'cart':{'read_only':True}
        }

    def validate(self,validated_data):
        qty=validated_data['qty']

        if qty>validated_data['product_item'].qty_in_stock:
            raise serializers.ValidationError('Quantity requested is more than available stock')
        if self.context['request'].user.username==validated_data['product_item'].seller:
            raise serializers.ValidationError('You cannot purchase from your own product')
        
        return validated_data
    
    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            cart, created = ShoppingCart.objects.get_or_create(user=user)
            validated_data['cart'] =cart
            print(validated_data)

        product_item = validated_data['product_item']
        qty = validated_data['qty']
        # Checking if the product is already in the cart
        existing_cart_item = ShoppingCartItem.objects.filter(cart=validated_data['cart'], product_item=product_item).first()
        if existing_cart_item:
            new_qty = existing_cart_item.qty + qty
            if new_qty > product_item.qty_in_stock:
                raise serializers.ValidationError('Quantity requested is more than available stock')

            existing_cart_item.qty = new_qty
            existing_cart_item.save()
        else:
            if qty > product_item.qty_in_stock:
                raise serializers.ValidationError('Quantity requested is more than available stock')

            cart_item = ShoppingCartItem.objects.create(**validated_data)
        
        return cart_item if not existing_cart_item else existing_cart_item
        
    def get_cart_owner(self,obj):
        return obj.cart.user.username
    
class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'


class OrderLineSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source='product_item.name',read_only=True)
    status=serializers.CharField(source='order_status',read_only=True)
    message=serializers.CharField(source='order_status.message',read_only=True)
    class Meta:
        model=OrderLine
        fields=['id','product_name','qty','price','order_status','status','message']
        extra_kwargs={
            'qty':{'read_only':True},
            'price':{'read_only':True},
            'order_status':{'allow_null':False,'write_only':True}
        }
    

class ShopOrderSerializer(serializers.ModelSerializer):
    order_items = OrderLineSerializer(many=True, source='orderline_set', read_only=True)
    payment_type=serializers.CharField(source='payment_method.payment_type',read_only=True)
    user_address=serializers.CharField(source='shipping_address.address_line1',read_only=True)
    shipping_details=ShippingMethodSerializer(source='shipping_method',read_only=True)
    class Meta:
        model = ShopOrder
        fields = ['id','order_date','payment_method','shipping_address','shipping_method','payment_type','user_address','shipping_details','order_items','order_total']
        extra_kwargs={
            'order_total':{'read_only':True},
            'payment_method':{'allow_null':False,'write_only':True},
            'shipping_address':{'allow_null':False,'write_only':True},
            'shipping_method':{'allow_null':False,'write_only':True}
        }
        ordering=['-order_date']

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        shipping_address=self.context['shipping_address']
        payment_method=self.context['payment_method']
        if shipping_address is not None:
            self.fields['shipping_address'].queryset=shipping_address
        if payment_method is not None:
            self.fields['payment_method'].queryset=payment_method
    
    @transaction.atomic
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        cart_items = ShoppingCartItem.objects.filter(cart__user=validated_data['user']).select_related('product_item')
        validated_data['order_date'] = timezone.now()
        if not cart_items.exists():
            raise serializers.ValidationError('Cart is empty')
        
        total_product_price = sum([item.product_item.price * item.qty for item in cart_items])
        shipping_cost = validated_data['shipping_method'].price

        promotion = Promotion.objects.filter(start_date__lte=validated_data['order_date'], end_date__gte=validated_data['order_date']).first()
        if promotion:
            cart_categories = cart_items.values_list('product_item__category', flat=True)
            product_categories = PromotionCategory.objects.filter(category__id__in=cart_categories)
            if product_categories.exists():
                for item in cart_items:
                    if item.product_item.category in [cat.category for cat in product_categories]:
                        discount_amount = item.product_item.price * item.qty * promotion.discount_rate / 100
                        total_product_price -= discount_amount

        validated_data['order_total'] = total_product_price + shipping_cost

        user_address = Address.objects.filter(id=validated_data['shipping_address'].address.id).first()

        if not user_address:
            raise serializers.ValidationError('Invalid shipping address')

        validated_data['shipping_address'] = user_address

        order = ShopOrder.objects.create(**validated_data)

        for item in cart_items:
            if item.qty > item.product_item.qty_in_stock:
                raise serializers.ValidationError(f'Quantity requested for {item.product_item.name} is more than available stock')

            OrderLine.objects.create(order=order, product_item=item.product_item, qty=item.qty, price=item.product_item.price)
            ProductItem.objects.filter(id=item.product_item.id).update(qty_in_stock=F('qty_in_stock') - item.qty)

        cart_items.delete()
        return order



    def to_representation(self, instance):
        response=super().to_representation(instance)
        response['order_date']=instance.order_date.strftime('%Y-%m-%d %H:%M:%S')
        return response
    