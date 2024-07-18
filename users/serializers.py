from rest_framework import serializers
from .models import SiteUser, Address, Country,UserAddress,UserPaymentMethod
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.utils import timezone
from sales_logistics.serializers import PaymentTypeSerializer

class UserRegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(style={'input_type':'password'},write_only=True,required=True)

    class Meta:
        model = SiteUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
        extra_kwargs = {'username':{'required':True},'email':{'required':False},'phone_number':{'required':True,'allow_blank':False}}
        
    def validate(self,validated_data):
        phone_number=validated_data.get('phone_number')

        if not phone_number:
            raise serializers.ValidationError('Phone number is required')
        if not len(phone_number)==10:
            raise serializers.ValidationError('Phone number must be 10 digits long')
        
        return validated_data
    
    def create(self,validated_data):
        password=validated_data.pop('password')
        user=SiteUser(**validated_data)
        user.set_password(password)
        user.save()
        self.instance = None
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        phone_number = data.get('phone_number')
        password = data.get('password')
        user = None
        if not (username or phone_number):
            raise serializers.ValidationError('Either username or phone number is required')
        if username:
            user = authenticate(username=username,password=password)
        elif phone_number:
            user = authenticate(username=phone_number,password=password)

        if not user:
            raise serializers.ValidationError('Invalid credentials')
        
        data['user'] = user
        return data

    def create(self, validated_data):
        return validated_data['user']
    
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    country_name = serializers.SerializerMethodField()
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(),write_only=True)
    

    class Meta:
        model = Address
        fields = ['id', 'unit_number', 'street_number', 'address_line1', 'address_line2', 'city', 'region', 'postal_code', 'country', 'country_name']

    def get_country_name(self, obj):
        return obj.country.country_name

class UserAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserAddress
        fields = '__all__'

    def get_user(self, obj):
        return obj.user.username

    def validate(self, attrs):
        address_data = attrs.get('address')
        user = self.context['request'].user

        if UserAddress.objects.filter(user=user, address__address_line1=address_data['address_line1'], address__city=address_data['city']).exists():
            raise serializers.ValidationError('Address already exists')

        return attrs

class ModifyAddressSerializer(serializers.ModelSerializer):
    address=AddressSerializer()
    user=serializers.SerializerMethodField()
    
    class Meta:

        model = UserAddress
        fields = '__all__'

    def get_user(self, obj):
        return obj.user.username
    
    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)
        if address_data:
            Address.objects.filter(id=instance.address.id).update(**address_data)
            instance.address.refresh_from_db()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance

class UserPaymentMethodSerializer(serializers.ModelSerializer):
    account_number=serializers.CharField(write_only=True,required=True,style={'input_type':'password'})
    expiry_date=serializers.DateField(required=True)
    payment_details=PaymentTypeSerializer(source='payment_type',read_only=True)

    class Meta:
        model=UserPaymentMethod
        fields=['id','payment_type','payment_details','provider','account_number','expiry_date','is_default']
        extra_kwargs={'payment_type':{'required':True,'allow_null':False,'write_only':True},'provider':{'required':True}}

    def validate_expiry_date(self,validated_data):

        if validated_data<timezone.now().date():
            raise serializers.ValidationError('Expiry date must not be in the past')
        return validated_data
            
    def create(self,validated_data):
        hasher=PBKDF2PasswordHasher()
        account_number=validated_data.pop('account_number')
        user=self.context['request'].user
        salt=hasher.salt()
        account_number=hasher.encode(account_number,salt)
        validated_data['account_number']=account_number
        validated_data['user']=user

        if validated_data['is_default']:
            UserPaymentMethod.objects.filter(user=user,is_default=True).update(is_default=False)
        return UserPaymentMethod.objects.create(**validated_data)
    
class UserPaymentUpdateSerializer(serializers.ModelSerializer):
    account_number=serializers.CharField(write_only=True,required=True,style={'input_type':'password'})
    class Meta:
        model=UserPaymentMethod
        fields=['id','provider','account_number','expiry_date','is_default']

    def update(self, instance, validated_data):
        account_number = validated_data.pop('account_number', None)
        if account_number:
            hasher = PBKDF2PasswordHasher()
            salt = instance.account_number.split('$')[2]  # Extract the salt from the existing hashed value
            hashed_account_number = hasher.encode(account_number, salt)
            # Verify the hashed account number
            if not hasher.verify(account_number, instance.account_number):
                raise serializers.ValidationError('Account number not valid')
            
            validated_data['account_number'] = hashed_account_number
        validated_data['payment_type'] = instance.payment_type
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)