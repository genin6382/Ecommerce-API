from django.urls import path
from . import views

urlpatterns=[
    path('payment-types/', views.PaymentTypesList.as_view(), name='payment-types-list'),
    path('shipping-methods/', views.ShippingMethodsList.as_view(), name='shipping-methods-list'),
    path('promotions/',views.PromotionList.as_view(),name='promotion-list'),
    path('promotions/<int:pk>/categories/',views.PromotionCategoryList.as_view(),name='promotion-category-list'),
]