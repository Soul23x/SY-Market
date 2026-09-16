from django.urls import path
from . import views


urlpatterns = [

    path('dashboard/payments/',views.payment_list,name='payment_list'),

    path('dashboard/payments/<int:payment_id>/',views.payment_detail,name='payment_detail'),

    path('dashboard/payments/<int:payment_id>/update-status/',views.payment_status_update,name='payment_status_update')

]