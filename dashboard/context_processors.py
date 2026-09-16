from accounts.models import PermissionType
from .views import has_permission

# importand for sending permissions to dashboard navbar template

def dashboard_permissions(request):
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {
            'can_access_store_ui': False,
            'can_access_products': False,
            'can_access_orders': False,
            'can_access_shipments': False,
            'can_access_payments': False,
        }
    else:
        return {
            'can_access_store_ui': has_permission(request.user, PermissionType.MANAGE_STORE_UI),
            'can_access_products': has_permission(request.user, PermissionType.MANAGE_PRODUCTS),
            'can_access_orders': has_permission(request.user, PermissionType.MANAGE_ORDERS),
            'can_access_shipments': has_permission(request.user, PermissionType.MANAGE_SHIPMENTS),
            'can_access_payments': has_permission(request.user, PermissionType.MANAGE_PAYMENTS),
        }