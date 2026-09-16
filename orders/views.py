from django.shortcuts import render,redirect,get_object_or_404
from .models import Order,OrderItem,OrderStatus
from payments.models import Payment,PaymentMethod,PaymentStatus
from store.models import Store
from cart.models import Cart
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from accounts.decorators import require_permission
from store.decorators import store_active_required
from accounts.models import PermissionType,Address
from django.contrib import messages
from django.core.paginator import Paginator
import datetime
from django.db import transaction
from django.views.decorators.http import require_POST
from shipping.models import Shipment,ShipmentStatus



@login_required
@require_permission(PermissionType.MANAGE_ORDERS)
def dashboard_order_list(request):

    context = {}

    search_query = request.GET.get('search')

    ongoing_orders_page = request.GET.get('ongoing_orders_page')

    fulfilled_orders_page = request.GET.get('fulfilled_orders_page')

    store = Store.objects.first()

    if search_query:
        ongoing_orders = Order.objects.filter((Q(order_status=OrderStatus.PENDING) | Q(order_status=OrderStatus.PROCESSING) | Q(order_status=OrderStatus.SHIPPED)) & (Q(order_number__icontains=search_query) | Q(customer__user__first_name__icontains=search_query) | Q(customer__user__last_name__icontains=search_query) | Q(customer__user__email__icontains=search_query) | Q(customer__user__phone_number__icontains=search_query) | Q(shipping_address__governorate__icontains=search_query) | Q(shipping_address__city__icontains=search_query)),store=store)
        
        fulfilled_orders = Order.objects.filter((Q(order_status=OrderStatus.REFUNDED) | Q(order_status=OrderStatus.CANCELLED) | Q(order_status=OrderStatus.DELIVERED)) & (Q(order_number__icontains=search_query) | Q(customer__user__first_name__icontains=search_query) | Q(customer__user__last_name__icontains=search_query) | Q(customer__user__email__icontains=search_query) | Q(customer__user__phone_number__icontains=search_query) | Q(shipping_address__governorate__icontains=search_query) | Q(shipping_address__city__icontains=search_query)),store=store)    
    else:
        ongoing_orders = Order.objects.filter(Q(order_status=OrderStatus.PENDING) | Q(order_status=OrderStatus.PROCESSING) | Q(order_status=OrderStatus.SHIPPED),store=store)

        fulfilled_orders = Order.objects.filter(Q(order_status=OrderStatus.REFUNDED) | Q(order_status=OrderStatus.CANCELLED) | Q(order_status=OrderStatus.DELIVERED),store=store)

    ongoing_paginator = Paginator(ongoing_orders,24)
    fulfilled_paginator = Paginator(fulfilled_orders,24)

    ongoing_page_obj = ongoing_paginator.get_page(ongoing_orders_page)
    fulfilled_page_obj = fulfilled_paginator.get_page(fulfilled_orders_page)

    context['ongoing_orders'] = ongoing_page_obj
    context['fulfilled_orders'] = fulfilled_page_obj

    return render(request,'orders/dashboard-order-list.html',context)



class OrderStateMachine:

    def __init__(self,current_state: OrderStatus):

        if isinstance(current_state, str):
            try:
                self.current_state = OrderStatus(current_state)
            except ValueError:
                self.current_state = current_state
        else:
            self.current_state = current_state
        
        self.transitions = {
            OrderStatus.PENDING: [OrderStatus.PROCESSING,OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED,OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED,OrderStatus.CANCELLED],
            OrderStatus.DELIVERED: [OrderStatus.REFUNDED],
            OrderStatus.CANCELLED: [],
            OrderStatus.REFUNDED: []
        }

    def available_next_states(self):
        return self.transitions.get(self.current_state,[])


    def available_next_states_choices(self):
        available_choices = []
        available_choices_list = self.available_next_states()
        for state in available_choices_list:
            available_choices.append((state,state.label))
        return available_choices


@login_required
@require_permission(PermissionType.MANAGE_ORDERS)
def dashboard_order_detail(request,order_id):

    order = get_object_or_404(Order,id=order_id,store=Store.objects.first())

    order_current_state = order.order_status

    order_state_machine = OrderStateMachine(order_current_state)

    order_status_choices = order_state_machine.available_next_states_choices()

    # also don't show status update button in template if no available next choices

    return render(request,'orders/dashboard-order-detail.html',{'order':order,'order_status_choices':order_status_choices})


#test
def restore_stock(order: Order):
    for item in order.order_items.all():
        item.product.stock += item.quantity
        item.product.save()
#test


@login_required
@require_permission(PermissionType.MANAGE_ORDERS)
@require_POST
@transaction.atomic
def order_status_update(request,order_id):

    order = get_object_or_404(Order,id=order_id,store=Store.objects.first())

    try:
        new_status = OrderStatus(request.POST.get('status'))
    except ValueError:
        messages.error(request,'Status Not Defined')
        return redirect('dashboard_order_detail',order_id)

    order_state_machine = OrderStateMachine(order.order_status)
    if new_status not in order_state_machine.available_next_states():
        messages.error(request,'Invalid Status Transition')
        return redirect('dashboard_order_detail',order_id)

    #test
    if new_status == OrderStatus.CANCELLED or new_status == OrderStatus.REFUNDED:
        payment = order.payment
        shipment = order.shipment
        if new_status == OrderStatus.CANCELLED:
            payment.mark_as(PaymentStatus.CANCELLED)
            shipment.mark_as(ShipmentStatus.CANCELLED)
        elif new_status == OrderStatus.REFUNDED:
            payment.mark_as(PaymentStatus.REFUNDED)
            shipment.mark_as(ShipmentStatus.RETURNED)
        restore_stock(order)
    #test

    order.mark_as(new_status)
    messages.success(request,'Status Updated')
    return redirect('dashboard_order_detail',order_id)




@login_required
def customer_order_list(request):

    search_query = request.GET.get('search')

    page = request.GET.get('page')

    if search_query:
        orders = Order.objects.filter(Q(order_number__icontains=search_query) | Q(order_status__icontains=search_query),store=Store.objects.first(),customer=request.user.customer)
    else:
        orders = Order.objects.filter(store=Store.objects.first(),customer=request.user.customer)

    paginator = Paginator(orders,24)
    page_obj = paginator.get_page(page)

    return render(request,'orders/customer-order-list.html',{'orders':page_obj})



@login_required
def customer_order_detail(request,order_id):

    order = get_object_or_404(Order,id=order_id,customer=request.user.customer)

    return render(request,'orders/customer-order-detail.html',{'order':order})



@login_required
@require_POST
@transaction.atomic
def customer_order_cancel(request,order_id):

    order = get_object_or_404(Order,id=order_id,customer=request.user.customer)

    if order.order_status != OrderStatus.PENDING or order.payment.payment_status != PaymentStatus.PENDING:
        messages.error(request,"Order Can't Be Cancelled In This Stage")
        return redirect('customer_order_detail',order_id)

    restore_stock(order)

    order.mark_as(OrderStatus.CANCELLED)
    order.payment.mark_as(PaymentStatus.CANCELLED)
    order.shipment.mark_as(ShipmentStatus.CANCELLED)

    messages.success(request,'Order Cancelled')
    return redirect('customer_order_detail',order_id)


@store_active_required
@login_required
def checkout(request):

    context = {}

    cart = Cart.objects.filter(customer=request.user.customer,store=Store.objects.first()).first()
    if not cart or not cart.cart_items.exists():
        messages.error(request,'Cart Empty')
        return redirect('cart_detail')
    cart_items = cart.cart_items.filter(product__is_active=True,product__category__is_active=True)

    for item in cart_items:
        item.max_increment = int(item.product.stock) - int(item.quantity)
        item.max_decrement = int(item.quantity) - 1

    addresses = request.user.customer.addresses.filter(is_order_snapshot=False)
    primary_address = addresses.filter(is_primary=True).first()

    context['cart_items']=cart_items
    context['addresses']=addresses
    context['primary_address']=primary_address

    return render(request,'orders/checkout.html',context)



def generate_order_number(id):
    
    year = str(datetime.date.today().year)
    month = str(datetime.date.today().month).zfill(2)
    return 'ORD'+'-'+year+month+'-'+str(id).zfill(5)


@store_active_required
@login_required
@require_POST
@transaction.atomic
def place_order(request):

    address_id = request.POST.get('address_id')

    if not address_id:
        messages.error(request,'No Address')
        return redirect('checkout')

    cart = request.user.customer.carts.filter(store=Store.objects.first()).first()

    if not cart or not cart.cart_items.exists():
        messages.error(request,'Cart Empty')
        return redirect('cart_detail')

    address = get_object_or_404(Address,id=address_id,customer=request.user.customer,is_order_snapshot=False)

    cart_items = cart.cart_items.all()
    for item in cart_items:
        if not item.product.is_active or not item.product.category.is_active:
            messages.error(request, f'"{item.product.name}" Is No Longer Available')
            return redirect('cart_detail')
        if item.quantity>item.product.stock:
            messages.error(request,f'Ordered Quantity Of Product "{item.product.name}" Is More Than Available Stock')
            return redirect('cart_detail')

    new_address = address
    new_address.id=None
    new_address.is_order_snapshot=True
    new_address.is_primary=False
    new_address.save()

    order = Order.objects.create(store=Store.objects.first(),customer=request.user.customer,order_number='temp',shipping_address=new_address,customer_phone_number=request.user.phone_number)
    order_number = generate_order_number(order.id)
    order.order_number=order_number
    order.save()

    for item in cart_items:
        order_item = OrderItem.objects.create(order=order,product=item.product,unit_price=item.product.price,quantity=item.quantity,product_name=item.product.name)
        item.product.stock -= item.quantity
        item.product.save()

    payment = Payment.objects.create(order=order,amount=order.total_price,payment_method=PaymentMethod.COD,transaction_id='')

    shipment = Shipment.objects.create(order=order,tracking_number=None)

    cart_items.delete()

    messages.success(request,'Order Placed')
    return redirect('customer_order_detail',order.id)