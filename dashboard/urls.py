from django.urls import path
from . import views


urlpatterns = [

    # Dashboard Home
    path('',views.dashboard_home,name='dashboard_home'),
    
]