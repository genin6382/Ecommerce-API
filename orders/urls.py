from django.urls import path
from . import views

urlpatterns=[
    #cart endpoints
    path('cart/items/', views.CartItem.as_view(), name='cart-item'),
    path('cart/items/<int:pk>/', views.CartItemDetail.as_view(), name='cart-item-detail'),
    #order endpoints
    path('status/', views.OrderStatusList.as_view(), name='order-status-list'),
    path('', views.ShopOrderList.as_view(), name='shop-order-list'),
    path('items/<int:pk>/', views.OrderLineList.as_view(), name='order-line-list'),
]