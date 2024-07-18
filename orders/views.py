from rest_framework import generics
from .models import OrderStatus, ShopOrder,ShoppingCart, ShoppingCartItem,OrderLine
from .serializers import ShoppingCartItemSerializer,OrderStatusSerializer,ShopOrderSerializer,OrderLineSerializer
from .permissions import IsCartOwner,IsOrderOwner
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from users.models import UserAddress,UserPaymentMethod
from products.models import ProductItem
from django.db.models import F
# Create your views here.

class CartItem(generics.ListCreateAPIView):
    serializer_class = ShoppingCartItemSerializer

    def get_queryset(self):
        cart=ShoppingCart.objects.filter(user=self.request.user).first()
        return ShoppingCartItem.objects.filter(cart=cart)
    def get_permissions(self):

        if self.request.method =='DELETE':
           permissions_classes=[IsCartOwner]
        else:
            permissions_classes=[IsAuthenticated]

        return [permission() for permission in permissions_classes]
    
    def delete(self,request,*args,**kwargs):
        cart=ShoppingCart.objects.filter(user=self.request.user).first()
        if cart:
            cart_items=ShoppingCartItem.objects.filter(cart=cart)
            if cart_items.exists():
                cart_items.delete()
                cart.delete()
                return Response({'message':'Cart deleted successfully'},status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message':'Cart is empty'},status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'message':'Cart does not exist'},status=status.HTTP_400_BAD_REQUEST)   

class CartItemDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ShoppingCartItemSerializer
    permission_classes=[IsCartOwner]
    def get_queryset(self):
        return ShoppingCartItem.objects.filter(id=self.kwargs['pk'])

class OrderStatusList(generics.ListCreateAPIView):
    queryset=OrderStatus.objects.all()
    serializer_class=OrderStatusSerializer
   

    def get_permissions(self):
         permission_classes=[IsAuthenticated]
         if self.request.method!='GET':
                permission_classes.append(IsAdminUser)
         return [permission() for permission in permission_classes]

class ShopOrderList(generics.ListCreateAPIView):
    serializer_class=ShopOrderSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        queryset=ShopOrder.objects.all().select_related('payment_method','shipping_address','shipping_method').prefetch_related('orderline_set__product_item__category','orderline_set__order_status')

        if not self.request.user.is_staff and not self.request.user.is_superuser:
            queryset=queryset.filter(user=self.request.user)
        return queryset
    
    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['shipping_address']=UserAddress.objects.filter(user=self.request.user)
        context['payment_method']=UserPaymentMethod.objects.filter(user=self.request.user)
        return context
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        shop_order = serializer.save()
        return Response({'message': f"Your order has been placed! Your order number is {shop_order.id}! Thank you for shopping with us"}, status=status.HTTP_201_CREATED)
         
class OrderLineList(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderLineSerializer

    def get_queryset(self):
        return OrderLine.objects.filter(id=self.kwargs['pk'])
    
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes=[IsOrderOwner | IsAdminUser]
        
        elif self.request.method == 'DELETE':
            order_item = OrderLine.objects.filter(id=self.kwargs['pk']).first()
            if order_item and order_item.order_status.status != 'Delivered':
                permission_classes = [IsOrderOwner]
            else:
                permission_classes = [IsAdminUser]
        else:
            permission_classes=[IsAdminUser]

        return [permission() for permission in permission_classes]
    
    def delete(self,request,*args,**kwargs):
        order_item=OrderLine.objects.filter(id=self.kwargs['pk']).first()
        order_id=order_item.order.id
        if order_item:
            ProductItem.objects.filter(id=order_item.product_item.id).update(qty_in_stock=F('qty_in_stock')+order_item.qty)
            price=order_item.price*order_item.qty
            ShopOrder.objects.filter(id=order_id).update(order_total=F('order_total')-price)
            order_item.delete()

            if not OrderLine.objects.filter(order=order_id).exists():
                ShopOrder.objects.filter(id=order_id).delete()
                
            return Response({'message':'Order deleted successfully'},status=status.HTTP_204_NO_CONTENT)
        return Response({'message':'Order does not exist'},status=status.HTTP_400_BAD_REQUEST)
    