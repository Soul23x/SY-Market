from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint,Q


# view makes sure amount equals to order total for now

class PaymentStatus(models.TextChoices):

    PENDING = "PENDING","Pending"

    PAID = "PAID","Paid"

    FAILED = "FAILED","Failed"

    REFUNDED = "REFUNDED","Refunded"

    CANCELLED = "CANCELLED","Cancelled"

class PaymentMethod(models.TextChoices):

    SHAMCASH = "SHAMCASH","Sham Cash"

    SYRIATELCASH = "SYRIATELCASH","Syriatel Cash"

    COD = "COD","Cash On Delivery"


class Payment(models.Model):

    order = models.OneToOneField('orders.Order',on_delete=models.PROTECT,related_name='payment')

    amount = models.DecimalField(max_digits=11,decimal_places=2,validators=[MinValueValidator(0)])

    payment_method = models.CharField(max_length=30,choices=PaymentMethod.choices)

    payment_status = models.CharField(max_length=30,choices=PaymentStatus.choices,default=PaymentStatus.PENDING)

    transaction_id = models.CharField(max_length=50,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def mark_as(self,status):
        self.payment_status=status
        self.save()

    def __str__(self):
        return f'Payment {self.transaction_id} for {self.order.order_number} ({self.payment_status})'

    class Meta:

        constraints = [UniqueConstraint(fields=['transaction_id'],condition=Q(payment_method=PaymentMethod.SHAMCASH) | Q(payment_method=PaymentMethod.SYRIATELCASH),name='unique_transaction_id_for_e_transaction')]