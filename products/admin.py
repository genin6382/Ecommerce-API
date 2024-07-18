from django.contrib import admin
from .models import ProductCategory,ProductItem,Variation,VariationOption,ProductConfiguration,Review
# Register your models here.
admin.site.register(ProductCategory)
admin.site.register(ProductItem)
admin.site.register(Variation)
admin.site.register(VariationOption)
admin.site.register(ProductConfiguration)
admin.site.register(Review)
