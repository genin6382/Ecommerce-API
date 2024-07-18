from rest_framework import generics
from .models import Address,UserAddress,UserPaymentMethod
from .serializers import UserRegisterSerializer,UserLoginSerializer,UserAddressSerializer,ModifyAddressSerializer,UserPaymentMethodSerializer,UserPaymentUpdateSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner,IsPaymentOwner
# Create your views here.

class Register(generics.CreateAPIView):
    serializer_class=UserRegisterSerializer

class Login(generics.CreateAPIView):
    serializer_class=UserLoginSerializer 
    #OPTIONAL 
    # def post(self,request):
    #     serializer=UserLoginSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     serializer_data=serializer.data
    #     return Response({"message":"Login Successful","data":serializer_data},status=status.HTTP_200_OK)

class CreateAddress(generics.ListCreateAPIView):
    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user).select_related('user','address__country')
    
    def perform_create(self, serializer):
        user = self.request.user
        is_default = serializer.validated_data.get('is_default', False)
        address_data = serializer.validated_data.pop('address')
        address, created = Address.objects.get_or_create(**address_data)

        if is_default:
            UserAddress.objects.filter(user=user,is_default=True).update(is_default=False)

        user_address = UserAddress.objects.create(address=address, user=user,is_default=is_default)
        serializer.instance = user_address

class EditDeleteAddress(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=ModifyAddressSerializer
    permission_classes = [IsAuthenticated,IsOwner]
    
    def get_queryset(self):
        try:
            return UserAddress.objects.filter(user=self.request.user,id=self.kwargs['pk']).select_related('user','address__country')
        except:
            return UserAddress.objects.none()
    
class UserPaymentMethodList(generics.ListCreateAPIView):
    serializer_class=UserPaymentMethodSerializer
    permission_classes=[IsAuthenticated,IsPaymentOwner]
    
    def get_queryset(self):
        return UserPaymentMethod.objects.filter(user=self.request.user).select_related('payment_type')

class UserPaymentEdit(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=UserPaymentUpdateSerializer
    permission_classes=[IsAuthenticated,IsPaymentOwner]

    def get_queryset(self):
        return UserPaymentMethod.objects.filter(user=self.request.user,id=self.kwargs['pk'])
    
