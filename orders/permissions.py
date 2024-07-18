from rest_framework.permissions import BasePermission

class IsCartOwner(BasePermission):
    def has_object_permission(self,request,view,obj):
        return obj.cart.user==request.user  and request.user.is_authenticated

class IsOrderOwner(BasePermission):
    def has_object_permission(self,request,view,obj):
        return obj.order.user==request.user and request.user.is_authenticated