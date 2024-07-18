from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('',views.ProductItemView.as_view(),name='product-item-list'),
    path('<int:pk>/',views.ProductItemDetail.as_view(),name='product-item-detail'),
    path('categories/',views.ProductCategoryList.as_view(),name='product-category-list'),
    path('categories/<int:category_id>/variations/',views.VariationList.as_view(),name='variation-list'),
    path('categories/<int:category_id>/variations/<int:variation_id>/options/',views.VariationOptionList.as_view(),name='variation-option-list'),
    path('<int:product_id>/configurations/',views.ProductConfigurationList.as_view(),name='product-configuration-list'),

    #product reviews
    path('<int:pk>/reviews/',views.ProductReview.as_view(),name='product-review-list'),
    path('reviews/<int:pk>/',views.ReviewDetail.as_view(),name='product-review-detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)