from rest_framework.permissions import BasePermission

class IsSellerOrAdmin(BasePermission):    
    def has_object_permission(self, request, view, obj):
        if hasattr(obj,'seller'):
            print(obj.seller)
            return obj.seller == request.user.username or request.user.is_staff
        
        elif hasattr(obj,'product_item'):
            print(obj.product_item.seller)
            return obj.product_item.seller == request.user.username or request.user.is_staff
        
        return False

class CanReview(BasePermission):
    def has_object_permission(self, request, view,obj):
        return obj.ordered_product.order.user == request.user