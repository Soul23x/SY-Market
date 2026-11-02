from accounts.models import PermissionType
from .views import has_permission

# important for sending permissions to dashboard navbar template

def dashboard_permissions(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {
            'can_access_store_ui': False,
            'can_access_products': False,
            'can_access_orders': False,
            'can_access_shipments': False,
            'can_access_payments': False,
            'is_store_owner': False,
        }
    else:
        return {
            'can_access_store_ui': has_permission(request.user, PermissionType.MANAGE_STORE_UI, request.store),
            'can_access_products': has_permission(request.user, PermissionType.MANAGE_PRODUCTS, request.store),
            'can_access_orders': has_permission(request.user, PermissionType.MANAGE_ORDERS, request.store),
            'can_access_shipments': has_permission(request.user, PermissionType.MANAGE_SHIPMENTS, request.store),
            'can_access_payments': has_permission(request.user, PermissionType.MANAGE_PAYMENTS, request.store),
            'is_store_owner': is_store_owner(request.user,request.store),
        }

def is_store_owner(user,store):
    return store is not None and store.owner.user == user