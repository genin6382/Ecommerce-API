from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('addresses/', views.CreateAddress.as_view(), name='addresses'),
    path('addresses/<int:pk>/',views.EditDeleteAddress.as_view(),name='edit-delete-address'),
#     path('user-reviews',views.UserReview.as_view(),name='user-reviews'),
    path('payment-methods/',views.UserPaymentMethodList.as_view(),name='user-payment-methods'),
    path('payment-methods/<int:pk>/',views.UserPaymentEdit.as_view(),name='user-payment-edit'),
]