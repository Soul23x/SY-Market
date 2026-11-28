from django.contrib import admin
from .models import Plan,Subscription,SubscriptionPayment

# Register your models here.
admin.site.register(Plan)

admin.site.register(Subscription)

@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'subscription', 'amount', 'method', 'sender_phone', 'status', 'created_at']
    list_filter = ['status', 'method']
    search_fields = ['transaction_id', 'sender_phone']