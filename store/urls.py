from django.urls import path
from . import views


urlpatterns = [

    path('dashboard/settings/',views.store_settings,name='store_settings'),

    path('dashboard/settings/toggle-active/',views.store_settings_toggle_active,name='store_settings_toggle_active'),


    path('dashboard/customization/',views.store_customization,name='store_customization'),
    
]