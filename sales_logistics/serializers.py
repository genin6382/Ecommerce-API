from rest_framework import serializers
from .models import PaymentType,ShippingMethod,Promotion,PromotionCategory

class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = '__all__'

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = '__all__'

class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = '__all__'
        extra_kwargs = {
            'discount_rate':{'required':True,'allow_null':False,'min_value':2,'max_value':100},
        }
    
    def validate(self,validated_data):
        if validated_data['start_date'] > validated_data['end_date']:
            raise serializers.ValidationError('End date must be after start date')
        
        return validated_data

class PromotionCategorySerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source='category.category_name',read_only=True)
    promotion_name=serializers.CharField(source='promotion.name',read_only=True)
    class Meta:
        model = PromotionCategory
        fields = ['id','category','promotion','category_name','promotion_name']
        extra_kwargs = {
            'category':{'write_only':True},
            'promotion':{'write_only':True},
        }
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        promotion=Promotion.objects.filter(id=self.context['pk'])
        if promotion:
            self.fields['promotion'].queryset=promotion
        else:
            raise serializers.ValidationError('Promotion not found')
    
    def validate(self,validated_data):
        if PromotionCategory.objects.filter(category=validated_data['category'],promotion=validated_data['promotion']):
            raise serializers.ValidationError('Category already in promotion')
        
        return validated_data