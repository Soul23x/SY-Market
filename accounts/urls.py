from django.urls import path
from . import views


urlpatterns = [

    path('register/',views.register_view,name='register'),

    path('login/',views.login_view,name='login'),

    path('logout/',views.logout_view,name='logout'),



    path('profile/', views.profile, name='profile'),

    path('profile/edit/', views.profile_edit, name='profile_edit'),

    path('profile/change-password/',views.change_password,name='change_password'),


    path('profile/addresses/',views.address_list,name='address_list'),

    path('profile/addresses/add/',views.address_add,name='address_add'),

    path('profile/addresses/<int:address_id>/edit/',views.address_edit,name='address_edit'),

    path('profile/addresses/<int:address_id>/make-primary/',views.address_make_primary,name='address_make_primary'),

    path('profile/addresses/<int:address_id>/delete/',views.address_delete,name='address_delete'),



    path('dashboard/employees/',views.employee_list,name='employee_list'),

    path('dashboard/employees/<int:employee_id>/',views.employee_detail,name='employee_detail'),

    path('dashboard/employees/add/',views.employee_add,name='employee_add'),

    path('dashboard/employees/<int:employee_id>/edit/',views.employee_edit,name='employee_edit'),

    path('dashboard/employees/<int:employee_id>/delete/',views.employee_delete,name='employee_delete'),

    path('dashboard/employees/<int:employee_id>/toggle-active/',views.employee_toggle_active,name='employee_toggle_active'),

    # no store address yet (even in model)

    #path('dashboard/settings/address/',views.store_address_list,name='store_address_list'),

    #path('dashboard/settings/address/add/',views.store_address_add,name='store_address_add'),

    #path('dashboard/settings/address/<int:address_id>/edit/',views.store_address_edit,name='store_address_edit'),

    #path('dashboard/settings/address/<int:address_id>/delete/',views.store_address_delete,name='store_address_delete'),

]