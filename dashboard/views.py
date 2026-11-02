from django.shortcuts import render
from accounts.decorators import require_employee
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from accounts.models import PermissionType
from catalog.models import Product,Category
from orders.models import Order,OrderStatus
from shipping.models import Shipment,ShipmentStatus
from payments.models import Payment,PaymentStatus
from store.models import Store
from accounts.models import Employee



def has_permission(user,permission,store):
    if store is None:
        return False
    employee = Employee.objects.filter(user=user,store=store,is_active=True).first()
    is_permitted_employee = employee is not None and employee.has_permission(permission)
    is_owner = (store.owner.user == user)
    return is_owner or is_permitted_employee



@login_required
@require_employee
def dashboard_home(request):

    context = {}
    permissions = []
    store=Store.objects.first()

    context['banner']=store.config.banner

    if has_permission(request.user,PermissionType.MANAGE_PRODUCTS):
        permissions.append(PermissionType.MANAGE_PRODUCTS)
        recently_added_products = Product.objects.filter(category__store=store).order_by('-created_at')[:10]
        recently_added_categories = Category.objects.filter(store=store).order_by('-created_at')[:10]
        context['recently_added_categories'] = recently_added_categories
        context['recently_added_products']=recently_added_products

    if has_permission(request.user,PermissionType.MANAGE_ORDERS):
        permissions.append(PermissionType.MANAGE_ORDERS)
        active_orders = Order.objects.filter(Q(order_status=OrderStatus.PENDING) | Q(order_status=OrderStatus.PROCESSING) | Q(order_status=OrderStatus.SHIPPED),store=store)
        context['active_orders'] = active_orders

    if has_permission(request.user,PermissionType.MANAGE_SHIPMENTS):
        permissions.append(PermissionType.MANAGE_SHIPMENTS)
        active_shipments = Shipment.objects.filter(Q(shipment_status=ShipmentStatus.PENDING) | Q(shipment_status=ShipmentStatus.PREPARING) | Q(shipment_status=ShipmentStatus.SHIPPED),order__store=store)
        context['active_shipments'] = active_shipments

    if has_permission(request.user,PermissionType.MANAGE_PAYMENTS):
        permissions.append(PermissionType.MANAGE_PAYMENTS)
        pending_payments = Payment.objects.filter(payment_status=PaymentStatus.PENDING,order__store=store)
        context['pending_payments'] = pending_payments

    context['permissions']=permissions
    return render(request,'dashboard/dashboard-home.html',context)