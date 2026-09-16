from django.urls import path
from . import views

urlpatterns = [

    path('cart/',views.cart_detail,name='cart_detail'),

    path('cart/add/<int:product_id>/',views.cart_item_add,name='cart_item_add'),

    path('cart/<int:cart_item_id>/increase/',views.cart_item_increase,name='cart_item_increase'),

    path('cart/<int:cart_item_id>/decrease/',views.cart_item_decrease,name='cart_item_decrease'),

    path('cart/<int:cart_item_id>/delete/',views.cart_item_delete,name='cart_item_delete'),

    path('cart/clear/',views.cart_clear,name='cart_clear')

]