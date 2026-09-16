from django.urls import path
from . import views

# category, product and review

urlpatterns = [

    path("", views.home, name="home"),

    path('categories/',views.category_list,name='category_list'),

    path('categories/<int:category_id>/',views.category_detail,name='category_detail'),


    path('products/',views.product_list,name='product_list'),

    path('products/<int:product_id>/',views.product_detail,name='product_detail'),


    path('products/<int:product_id>/reviews/add/',views.review_add,name='review_add'),

    path('products/<int:product_id>/reviews/<int:review_id>/edit/',views.review_edit,name='review_edit'),

    path('products/<int:product_id>/reviews/<int:review_id>/delete/',views.review_delete,name='review_delete'),


    path('dashboard/categories/',views.dashboard_category_list,name='dashboard_category_list'),
        
    path('dashboard/categories/<int:category_id>/',views.dashboard_category_detail,name='dashboard_category_detail'),

    path('dashboard/categories/add/',views.category_add,name='category_add'),
    
    path('dashboard/categories/<int:category_id>/edit/',views.category_edit,name='category_edit'),
    
    path('dashboard/categories/<int:category_id>/delete/',views.category_delete,name='category_delete'),

    path('dashboard/categories/<int:category_id>/toggle-active/', views.category_toggle_active, name='category_toggle_active'),


    path('dashboard/products/',views.dashboard_product_list,name='dashboard_product_list'),
    
    path('dashboard/products/<int:product_id>/',views.dashboard_product_detail,name='dashboard_product_detail'),

    path('dashboard/products/add/',views.product_add,name='product_add'),
    
    path('dashboard/products/<int:product_id>/edit/',views.product_edit,name='product_edit'),
    
    path('dashboard/products/<int:product_id>/delete/',views.product_delete,name='product_delete'),

    path('dashboard/products/<int:product_id>/toggle-active/',views.product_toggle_active,name='product_toggle_active'),


    path('dashboard/products/<int:product_id>/images/add/',views.product_image_add,name='product_image_add'),

    path('dashboard/products/<int:product_id>/images/<int:product_image_id>/delete/',views.product_image_delete,name='product_image_delete')

]