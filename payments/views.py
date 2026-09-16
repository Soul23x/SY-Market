from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import PaymentStatus,Payment
from accounts.decorators import require_permission
from accounts.models import PermissionType
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from store.models import Store
from django.views.decorators.http import require_POST
from django.db import transaction
from orders.views import restore_stock
from shipping.models import Shipment,ShipmentStatus
from orders.models import Order,OrderStatus


@login_required
@require_permission(PermissionType.MANAGE_PAYMENTS)
def payment_list(request):

    search_query = request.GET.get('search')
    page = request.GET.get('page')

    if search_query:
        payments = Payment.objects.filter(
            Q(order__order_number__icontains=search_query) | 
            Q(transaction_id__icontains=search_query) |
            Q(payment_method__icontains=search_query) |
            Q(payment_status__icontains=search_query),
            order__store = Store.objects.first()
            )
    else:
        payments = Payment.objects.filter(order__store = Store.objects.first()).order_by('-created_at')

    paginator = Paginator(payments,24)
    page_obj = paginator.get_page(page)

    return render(request,'payments/payment-list.html',{'payments':page_obj})


class PaymentStateMachine:

    def __init__(self,current_state: PaymentStatus):

        if isinstance(current_state, str):
            try:
                self.current_state = PaymentStatus(current_state)
            except ValueError:
                self.current_state = current_state
        else:
            self.current_state = current_state
        
        self.transitions = {
            PaymentStatus.PENDING: [PaymentStatus.PAID,PaymentStatus.CANCELLED,PaymentStatus.FAILED],
            PaymentStatus.PAID: [PaymentStatus.REFUNDED],
            PaymentStatus.FAILED: [PaymentStatus.PENDING],
            PaymentStatus.REFUNDED: [],
            PaymentStatus.CANCELLED: []
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
@require_permission(PermissionType.MANAGE_PAYMENTS)
def payment_detail(request,payment_id):

    payment = get_object_or_404(Payment,id=payment_id,order__store=Store.objects.first())

    payment_state_machine = PaymentStateMachine(payment.payment_status)

    payment_status_choices = payment_state_machine.available_next_states_choices()

    return render(request,'payments/payment-detail.html',{'payment':payment,'payment_status_choices':payment_status_choices})



@login_required
@require_permission(PermissionType.MANAGE_PAYMENTS)
@require_POST
@transaction.atomic
def payment_status_update(request,payment_id):

    payment = get_object_or_404(Payment,id=payment_id,order__store=Store.objects.first())

    try:
        status = PaymentStatus(request.POST.get('status'))
    except ValueError:
        messages.error(request,'Invalid Status')
        return redirect('payment_detail',payment_id)

    payment_state_machine = PaymentStateMachine(payment.payment_status)
    if not status in payment_state_machine.available_next_states():
        messages.error(request,'Invalid Status Transition')
        return redirect('payment_detail',payment_id)

    if status in [PaymentStatus.REFUNDED,PaymentStatus.CANCELLED]:
        order = payment.order
        shipment = payment.order.shipment
        if status == PaymentStatus.CANCELLED:
            order.mark_as(OrderStatus.CANCELLED)
            shipment.mark_as(ShipmentStatus.CANCELLED)
        elif status == PaymentStatus.REFUNDED:
            order.mark_as(OrderStatus.REFUNDED)
            shipment.mark_as(ShipmentStatus.RETURNED)
        restore_stock(order)
                

    payment.mark_as(status)
    messages.success(request,'Payment Status Updated')
    return redirect('payment_detail',payment_id)

