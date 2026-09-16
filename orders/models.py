from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum,F



class OrderStatus(models.TextChoices):

    PENDING = "PENDING","Pending"

    PROCESSING = "PROCESSING","Processing"

    SHIPPED = "SHIPPED","Shipped"

    DELIVERED = "DELIVERED","Delivered"

    CANCELLED = "CANCELLED","Cancelled"

    REFUNDED = "REFUNDED","Refunded"

# questionable design, so many business rules involved
#later, add an is_active helper method, if you plan to make a state machine whatever that is

class Order(models.Model):

    store = models.ForeignKey('store.Store',on_delete=models.PROTECT,related_name='orders')

    customer = models.ForeignKey('accounts.Customer',on_delete=models.PROTECT,related_name='orders')

    order_number = models.CharField(max_length=30,unique=True)

    # view sets this as is_order_snapshot = True
    shipping_address = models.ForeignKey('accounts.Address',on_delete=models.PROTECT,related_name='orders')

    order_status = models.CharField(max_length=30,choices=OrderStatus.choices,default=OrderStatus.PENDING)
    
    created_at = models.DateTimeField(auto_now_add=True)

    # view updates this if the customer changes his number mid-order(checks if he has active orders)
    customer_phone_number = models.CharField(max_length=15)

    @property
    def total_price(self):
        total = self.order_items.aggregate(total=Sum(F('unit_price') * F('quantity')))['total']
        return total or 0

    @property
    def is_pending(self):
        return self.order_status==OrderStatus.PENDING

    def mark_as(self,status):
        self.order_status=status
        self.save()

    def __str__(self):
            return f'Order {self.order_number} ({self.order_status})'

    class Meta:
        ordering = ['-created_at']



class OrderItem(models.Model):

    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='order_items')

    product = models.ForeignKey('catalog.Product',on_delete=models.PROTECT,related_name='order_items')

    # view copies the current price on checkout into this same in product name and customer phone number
    unit_price = models.DecimalField(max_digits=11,decimal_places=2,validators=[MinValueValidator(0)])
    
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    product_name = models.CharField(max_length=50)

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.product_name} x{self.quantity} : {self.subtotal}'