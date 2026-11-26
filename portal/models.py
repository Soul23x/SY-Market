from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone



class Plan(models.Model):

    name = models.CharField(max_length=30,unique=True)

    price = models.DecimalField(max_digits=11,decimal_places=2,validators=[MinValueValidator(0)])

    max_products = models.IntegerField(null=True,blank=True)

    max_employees = models.IntegerField(null=True,blank=True)

    allows_custom_theme = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SubscriptionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACTIVE = "ACTIVE", "Active"


class Subscription(models.Model):

    store = models.OneToOneField('store.Store',on_delete=models.CASCADE,related_name='subscription')

    plan = models.ForeignKey(Plan,on_delete=models.PROTECT,related_name='subscriptions')

    status = models.CharField(max_length=30,choices=SubscriptionStatus.choices,default=SubscriptionStatus.PENDING)

    started_at = models.DateTimeField(null=True,blank=True)

    expires_at = models.DateTimeField(null=True,blank=True)

    @property
    def is_expired(self):
        if self.expires_at is None:
            return False
        if self.expires_at < timezone.now():
            return True
        return False

    def __str__(self):
        return f'{self.store.name} - {self.plan.name}'