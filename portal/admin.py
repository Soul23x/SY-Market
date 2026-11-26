from django.contrib import admin
from .models import Plan,Subscription,SubscriptionPayment

# Register your models here.
admin.site.register(Plan)

admin.site.register(Subscription)

admin.site.register(SubscriptionPayment)