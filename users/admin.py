from django.contrib import admin
from .models import SiteUser,Country,Address,UserAddress,UserPaymentMethod
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = SiteUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number',)}),
    )

admin.site.register(SiteUser, CustomUserAdmin)

admin.site.register(Country)
admin.site.register(Address)
admin.site.register(UserAddress)
admin.site.register(UserPaymentMethod)
