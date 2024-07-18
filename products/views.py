from .models import ProductCategory,ProductItem, Variation, VariationOption, ProductConfiguration, Review
from rest_framework import generics
from .serializers import ProductCategorySerializer,ProductItemSerializer, VariationSerializer, VariationOptionSerializer, ProductConfigurationSerializer, ReviewSerializer
from rest_framework.permissions import IsAdminUser,AllowAny,IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import IsSellerOrAdmin,CanReview
from rest_framework.permissions import SAFE_METHODS
from orders.models import OrderLine
# Create your views here.

class ProductCategoryList(generics.ListCreateAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    parser_classes=[MultiPartParser, FormParser]
    
    def get_permissions(self):
        permission_classes = [AllowAny]

        if self.request.method !='GET':
           permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

class ProductItemView(generics.ListCreateAPIView):
    queryset = ProductItem.objects.all().select_related('category')
    serializer_class = ProductItemSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]

        if self.request.method == 'POST':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

class ProductItemDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductItemSerializer
    permission_classes = [IsAuthenticated,IsSellerOrAdmin]

    def get_queryset(self):
        return ProductItem.objects.filter(id=self.kwargs['pk']).select_related('category')
    

class VariationList(generics.ListCreateAPIView):
    serializer_class=VariationSerializer
    def get_queryset(self):
        return Variation.objects.filter(category=self.kwargs['category_id'])
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        
        return [permission() for permission in permission_classes]
        
    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['category_id']=self.kwargs['category_id']
        return context

class VariationOptionList(generics.ListCreateAPIView):
    serializer_class=VariationOptionSerializer

    def get_queryset(self):
        category=ProductCategory.objects.get(id=self.kwargs['category_id'])
        category_variation=Variation.objects.filter(category=category)
        variation_by_id=Variation.objects.get(id=self.kwargs['variation_id'])
        if variation_by_id in category_variation:
            return VariationOption.objects.filter(variation=variation_by_id)
        else:
            return []
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['variation_id']=self.kwargs['variation_id']
        return context

class ProductConfigurationList(generics.ListCreateAPIView):
    serializer_class=ProductConfigurationSerializer

    def get_queryset(self):
        return ProductConfiguration.objects.filter(product_item=self.kwargs['product_id']).select_related('product_item','variation_option')
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsSellerOrAdmin]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['product_id']=self.kwargs['product_id']

        product=ProductItem.objects.get(id=self.kwargs['product_id'])
        category=product.category
        variations=Variation.objects.filter(category=category)
        variation_options=VariationOption.objects.filter(variation__in=variations).select_related('variation')
        context['variation_option']=variation_options
        return context
    
class ProductReview(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    
    def get_queryset(self):
        product_item = ProductItem.objects.get(id=self.kwargs['pk'])
        if Review.objects.filter(ordered_product__product_item=product_item).exists():
            return Review.objects.filter(ordered_product__product_item=product_item)
        return Review.objects.none()

    def get_permissions(self):
        permission_classes = []
        if self.request.method != 'GET':
            permission_classes = [IsAuthenticated, CanReview]
        return [permission() for permission in permission_classes]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_item = ProductItem.objects.get(id=self.kwargs['pk'])
        ordered_product = None
        if self.request.user.is_authenticated:
            ordered_product = OrderLine.objects.filter(product_item=product_item, order__user=self.request.user).first()
        context['ordered_product'] = ordered_product
        return context

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=ReviewSerializer
    permission_classes=[IsAuthenticated,CanReview]

    def get_queryset(self):
        return Review.objects.filter(id=self.kwargs['pk']).select_related('user','ordered_product')
    
    