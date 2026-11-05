from django.shortcuts import render,redirect,get_object_or_404
from accounts.decorators import require_permission
from django.contrib.auth.decorators import login_required
from .models import Shipment,ShipmentStatus
from accounts.models import PermissionType
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from orders.views import restore_stock
from payments.models import PaymentStatus
from orders.models import OrderStatus


@login_required
@require_permission(PermissionType.MANAGE_SHIPMENTS)
def shipment_list(request):

    search_query = request.GET.get('search')

    page = request.GET.get('page')

    if search_query:
        shipments = Shipment.objects.filter(Q(tracking_number__icontains=search_query) | Q(shipment_status__icontains=search_query), order__store=request.store).order_by('-created_at')
    else:
        shipments = Shipment.objects.filter(order__store=request.store).order_by('-created_at')

    paginator = Paginator(shipments,24)

    page_obj = paginator.get_page(page)

    return render(request,'shipping/shipment-list.html',{'shipments':page_obj})



@login_required
@require_permission(PermissionType.MANAGE_SHIPMENTS)
@require_POST
def shipment_assign_tracking_number(request,shipment_id):

    shipment = get_object_or_404(Shipment,id=shipment_id,order__store=request.store)

    tracking_number = request.POST.get('tracking_number').strip()

    if not tracking_number:
        messages.error(request,"Tracking Number Is Empty")
        return redirect('shipment_detail',shipment_id)

    shipment.assign_tracking_number(tracking_number)
    # removed marking as shipped
    
    messages.success(request,'Shipment Tracking Number Assigned')
    return redirect('shipment_detail',shipment_id)



class ShipmentStateMachine:

    def __init__(self,current_state: ShipmentStatus):

        if isinstance(current_state, str):
            try:
                self.current_state = ShipmentStatus(current_state)
            except ValueError:
                self.current_state = current_state
        else:
            self.current_state = current_state
        
        self.transitions = {
            ShipmentStatus.PENDING: [ShipmentStatus.PREPARING,ShipmentStatus.CANCELLED],
            ShipmentStatus.PREPARING: [ShipmentStatus.SHIPPED,ShipmentStatus.CANCELLED],
            ShipmentStatus.SHIPPED: [ShipmentStatus.DELIVERED,ShipmentStatus.CANCELLED],
            ShipmentStatus.DELIVERED: [ShipmentStatus.RETURNED],
            ShipmentStatus.CANCELLED: [],
            ShipmentStatus.RETURNED: []
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
@require_permission(PermissionType.MANAGE_SHIPMENTS)
def shipment_detail(request,shipment_id):

    shipment = get_object_or_404(Shipment,id=shipment_id,order__store=request.store)

    shipment_state_machine = ShipmentStateMachine(shipment.shipment_status)

    shipment_status_choices = shipment_state_machine.available_next_states_choices()

    return render(request,'shipping/shipment-detail.html',{'shipment':shipment,'shipment_status_choices':shipment_status_choices})



@login_required
@require_permission(PermissionType.MANAGE_SHIPMENTS)
@require_POST
@transaction.atomic
def shipment_status_update(request,shipment_id):

    shipment = get_object_or_404(Shipment,id=shipment_id,order__store=request.store)

    try:
        new_status = ShipmentStatus(request.POST.get('status'))
    except ValueError:
        messages.error(request,'Status Not Defined')
        return redirect('shipment_detail',shipment_id)

    shipment_state_machine = ShipmentStateMachine(shipment.shipment_status)

    if new_status not in shipment_state_machine.available_next_states():
        messages.error(request,'Invalid Status Transition')
        return redirect('shipment_detail',shipment_id)


    if new_status == ShipmentStatus.CANCELLED or new_status == ShipmentStatus.RETURNED:
        order = shipment.order
        payment = shipment.order.payment
        if new_status == ShipmentStatus.CANCELLED:
            payment.mark_as(PaymentStatus.CANCELLED)
            order.mark_as(OrderStatus.CANCELLED)
        elif new_status == ShipmentStatus.RETURNED:
            payment.mark_as(PaymentStatus.REFUNDED)
            order.mark_as(OrderStatus.REFUNDED)
        restore_stock(order)


    shipment.mark_as(new_status)
    messages.success(request,'Shipment Status Updated')
    return redirect('shipment_detail',shipment_id)
