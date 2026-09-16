from django.urls import path
from . import views

urlpatterns = [

    path('orders/',views.customer_order_list,name='customer_order_list'),

    path('orders/<int:order_id>/',views.customer_order_detail,name='customer_order_detail'),

    path('orders/<int:order_id>/cancel/',views.customer_order_cancel,name='customer_order_cancel'),
    


    path('checkout/',views.checkout,name='checkout'),

    #belong in accounts, an address add url, an accounts view
    #path('checkout/address/',views.checkout_address_update,name='checkout_address_update'),

    #not in GP1
    #path('checkout/payment/',views.checkout_payment,name='checkout_payment'),

    # assumes payment is COD
    path('checkout/place-order/',views.place_order,name='place_order'),



    path('dashboard/orders/',views.dashboard_order_list,name='dashboard_order_list'),

    path('dashboard/orders/<int:order_id>/',views.dashboard_order_detail,name='dashboard_order_detail'),

    path('dashboard/orders/<int:order_id>/update-status/',views.order_status_update,name='order_status_update')

]