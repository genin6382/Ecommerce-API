from rest_framework import generics
from .models import PaymentType,ShippingMethod,Promotion,PromotionCategory
from .serializers import PaymentTypeSerializer,ShippingMethodSerializer,PromotionSerializer,PromotionCategorySerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser,SAFE_METHODS,AllowAny
from django.utils import timezone
# Create your views here.
class PaymentTypesList(generics.ListCreateAPIView):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method!='GET':
            permission_classes.append(IsAdminUser)
        return [permission() for permission in permission_classes]
    
class ShippingMethodsList(generics.ListCreateAPIView):
    queryset = ShippingMethod.objects.all()
    serializer_class = ShippingMethodSerializer
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method!='GET':
            permission_classes.append(IsAdminUser)
        return [permission() for permission in permission_classes]
    
class PromotionList(generics.ListCreateAPIView):
    serializer_class=PromotionSerializer

    def get_queryset(self):
        return Promotion.objects.filter(start_date__lte=timezone.now(),end_date__gte=timezone.now())
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes=[AllowAny]
        else:
            permission_classes=[IsAdminUser]

        return [permission() for permission in permission_classes]
    
class PromotionCategoryList(generics.ListCreateAPIView):
    serializer_class=PromotionCategorySerializer
    permission_classes=[IsAdminUser]
    
    def get_queryset(self):
        return PromotionCategory.objects.filter(promotion=self.kwargs['pk']).select_related('promotion','category')
    def get_serializer_context(self):
        context=super().get_serializer_context()
        context['pk']=self.kwargs['pk']
        return context
    