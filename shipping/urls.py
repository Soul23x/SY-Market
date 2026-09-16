from django.urls import path
from . import views


urlpatterns = [

    path('dashboard/shipments/',views.shipment_list,name='shipment_list'),

    path('dashboard/shipments/<int:shipment_id>/',views.shipment_detail,name='shipment_detail'),


    path('dashboard/shipments/<int:shipment_id>/update-status/',views.shipment_status_update,name='shipment_status_update'),

    path('dashboard/shipments/<int:shipment_id>/assign-tracking-number/',views.shipment_assign_tracking_number,name='shipment_assign_tracking_number')

]