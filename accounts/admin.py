from django.contrib import admin
from .models import User,StoreOwner,Customer,Employee,Permission,Address


admin.site.register(User)
admin.site.register(StoreOwner)
admin.site.register(Customer)
admin.site.register(Employee)
admin.site.register(Permission)
admin.site.register(Address)