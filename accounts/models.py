from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import UniqueConstraint,Q

class User(AbstractUser):

    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=15)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class StoreOwner(models.Model):

    user = models.OneToOneField(User,on_delete = models.CASCADE,related_name='store_owner')

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)   # separate from User

    def __str__(self):
        return f'{self.user.username} (Owner)'



class Customer(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='customer')

    def __str__(self):
        return self.user.username



class Employee(models.Model):

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='employee')

    #change later if store owner can own multiple stores
    #store = models.ForeignKey('store.Store',on_delete=models.CASCADE,related_name='employees')

    permissions = models.ManyToManyField("Permission",related_name='employees')

    assigned_by = models.ForeignKey(StoreOwner,on_delete=models.PROTECT,related_name='employees')

    joined_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)   # separate from User

    @property
    def store(self):
        return self.assigned_by.store

    def has_permission(self, permission_type):
        return self.permissions.filter(permission_type=permission_type).exists()

    def __str__(self):
            return f'{self.user.username} (Employee)'

    

class PermissionType(models.TextChoices):

    MANAGE_PRODUCTS = "MANAGE_PRODUCTS","Manage Products"

    MANAGE_ORDERS = "MANAGE_ORDERS","Manage Orders"

    MANAGE_SHIPMENTS = "MANAGE_SHIPMENTS","Manage Shipments"

    MANAGE_PAYMENTS = "MANAGE_PAYMENTS","Manage Payments"

    MANAGE_STORE_UI = "MANAGE_STORE_UI","Manage Store UI"


class Permission(models.Model):

    permission_type=models.CharField(max_length=50,choices=PermissionType.choices,unique=True)

    def __str__(self):
        return self.get_permission_type_display()



class AddressGovernorate(models.TextChoices):

    DAMASCUS = "DAMASCUS","Damascus"

    ALEPPO = "ALEPPO","Aleppo"

    DARAA = "DARAA","Daraa"

    DEIR_EZ_ZOR = "DEIR_EZ_ZOR","Deir Ez-Zor"

    HAMA = "HAMA","Hama"

    AL_HASAKAH = "AL_HASAKAH","Al-Hasakah"

    HOMS = "HOMS","Homs"

    IDLIB = "IDLIB","Idlib"

    LATAKIA = "LATAKIA","Latakia"

    QUNEITRA = "QUNEITRA","Quneitra"

    RAQQA = "RAQQA","Raqqa"

    RIF_DIMASHQ = "RIF_DIMASHQ","Rif Dimashq"

    AS_SUWAYDA = "AS_SUWAYDA","As-suwayda"

    TARTUS = "TARTUS","Tartus"



class Address(models.Model):

    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='addresses')

    governorate = models.CharField(max_length=30,choices=AddressGovernorate.choices)

    city = models.CharField(max_length=30)

    street = models.CharField(max_length=30)

    building = models.CharField(max_length=30)

    unit = models.CharField(max_length=50,blank=True,null=True)

    notes = models.CharField(max_length=150,blank=True,null=True)

    # if yes address is historical
    is_order_snapshot = models.BooleanField(default=False)

    # view makes sure first customer address's is_primary is set as True, this is the customer live address (not made by order) 
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.governorate} - {self.city} - {self.street}'

    class Meta:
        verbose_name_plural = 'Addresses'
        # unique customer if is_primary=True :)
        constraints = [UniqueConstraint(fields=['customer'],condition=Q(is_primary=True),name='unique_primary_address_per_customer')]