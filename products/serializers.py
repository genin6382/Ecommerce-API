from rest_framework import serializers
from .models import ProductCategory,ProductItem, Variation, VariationOption, ProductConfiguration,Review
from orders.models import OrderLine
class ProductCategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, use_url=True, allow_empty_file=True, required=False)
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductItemSerializer(serializers.ModelSerializer):
    product_image = serializers.URLField(max_length=None, allow_blank=True,required=False)
    category_name=serializers.CharField(source='category.category_name',read_only=True)
    class Meta:
        model = ProductItem
        fields = ['id','category','category_name','name','description','product_image','seller','SKU','qty_in_stock','price','date_added']

        extra_kwargs={
            'qty_in_stock':{'allow_null':False,'min_value':1},
            'price':{'allow_null':False,'min_value':20},
            'name':{'allow_null':False},
            'SKU':{'read_only':True},
            'category':{'write_only':True},
            'seller':{'read_only':True},
        }

        REQUIRED_FIELDS = ['name','description','qty_in_stock','price']
    
    def create(self,validated_data):
        seller=self.context['request'].user.username
        validated_data['seller']=seller
        product_item=ProductItem.objects.create(**validated_data)
        return product_item

class VariationSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source='category.category_name',read_only=True)
    class Meta:
        model=Variation
        fields=['id','name','category_name']
    
    def create(self,validated_data):
        category_id=self.context['category_id']
        variation=Variation.objects.create(category_id=category_id,**validated_data)
        return variation
    
class VariationOptionSerializer(serializers.ModelSerializer):
    variation_name=serializers.CharField(source='variation.name',read_only=True)
    class Meta:
        model=VariationOption
        fields=['id','variation_name','value']

    def create(self,validated_data):
        variation_id=self.context['variation_id']
        variation_option=VariationOption.objects.create(variation_id=variation_id,**validated_data)
        return variation_option
    
class ProductConfigurationSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source='product_item.name',read_only=True)
    variation_name=serializers.CharField(source='variation_option.value',read_only=True)

    class Meta:
        model=ProductConfiguration
        fields=['product_name','id','variation_option','variation_name','qty_in_stock','out_of_stock']

        extra_kwargs={
            'qty_in_stock':{'allow_null':False,'min_value':0},
            'variation_option':{'write_only':True},
            'out_of_stock':{'read_only':True},
        }
    
    def __init__(self,*args,**kwargs):
        
        super(ProductConfigurationSerializer,self).__init__(*args,**kwargs)
        variation_option=self.context['variation_option']
        if variation_option is not None:
            self.fields['variation_option'].queryset=variation_option

    def validate(self,validated_data):
        product_item_id=self.context['product_id']
        item_qty=sum([prod.qty_in_stock for prod in ProductItem.objects.filter(id=product_item_id)])
        conf_qty=sum([conf.qty_in_stock for conf in ProductConfiguration.objects.filter(product_item_id=product_item_id)])

        if item_qty<conf_qty+validated_data['qty_in_stock']:
            raise serializers.ValidationError('Quantity in stock exceeds available stock')
        
        if validated_data['variation_option'] not in self.context['variation_option']:
            raise serializers.ValidationError('This item does not support the selected variation option')
        return validated_data

    def create(self,validated_data):
        product_item_id=self.context['product_id']
        product_conf=ProductConfiguration.objects.filter(product_item_id=product_item_id,variation_option=validated_data['variation_option']).first()

        if product_conf:
            new_quantity=validated_data['qty_in_stock']+product_conf.qty_in_stock
            product_conf.qty_in_stock=new_quantity
            product_conf.save()
            return product_conf
        
        final_product_configuration=ProductConfiguration.objects.create(product_item_id=product_item_id,**validated_data)
        return final_product_configuration

class ReviewSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source='user.username',read_only=True)
    
    class Meta:
        model=Review
        fields=['id','username','rating_value','comment']
        extra_kwargs={
            'rating_value':{'allow_null':False},
            'comment':{'allow_null':False},
        }

    def create(self,validated_data):
        user=self.context['request'].user
        
        if not user.is_authenticated:
            raise serializers.ValidationError('You must be logged in to submit a review.')
        
        validated_data['user']=user
        validated_data['ordered_product']=self.context['ordered_product']

        if validated_data['ordered_product'] is None:
            raise serializers.ValidationError('You can only review products you have ordered')
        
        return Review.objects.create(**validated_data)
    