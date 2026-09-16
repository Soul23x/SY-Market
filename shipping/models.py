from django.db import models


class ShipmentStatus(models.TextChoices):

    PENDING = "PENDING","Pending"

    PREPARING = "PREPARING","Preparing"

    SHIPPED = "SHIPPED","Shipped"

    DELIVERED = "DELIVERED","Delivered"

    CANCELLED = "CANCELLED","Cancelled"

    RETURNED = "RETURNED","Returned"



class Shipment(models.Model):

    order = models.OneToOneField('orders.Order',on_delete=models.PROTECT,related_name='shipment')

    tracking_number = models.CharField(max_length=50,unique=True,null=True)

    shipment_status = models.CharField(max_length=20,choices=ShipmentStatus.choices,default=ShipmentStatus.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def mark_as(self,status):
        self.shipment_status=status
        self.save()

    def assign_tracking_number(self,number):
        self.tracking_number=number
        self.save()

    def __str__(self):
        if self.tracking_number:
            return f'Shipment {self.tracking_number} for {self.order.order_number} ({self.shipment_status})'
        return f'Shipment for {self.order.order_number} ({self.shipment_status})'