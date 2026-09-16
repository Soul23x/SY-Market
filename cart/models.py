from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum, F


class Cart(models.Model):

    customer = models.ForeignKey('accounts.Customer',on_delete=models.CASCADE,related_name='carts')

    store = models.ForeignKey('store.Store',on_delete=models.CASCADE,related_name='carts')

    created_at = models.DateTimeField(auto_now_add=True)

    # aggregates return a dict
    @property
    def cart_total(self):
        # chack if this works
        return self.cart_items.aggregate(total=Sum(F('product__price') * F('quantity')))['total'] or 0
        #if self.cart_items.exists():
            #return self.cart_items.aggregate(total=Sum(F('product__price') * F('quantity')))['total']
        #else :
            #return 0

    def __str__(self):
        return f'{self.customer}\'s {self.store} cart'

    class Meta:

        constraints = [models.UniqueConstraint(fields=['customer','store'],name='unique_customer_cart_per_store')]


# override save() later to insure the product is from the same store as the cart
class CartItem(models.Model):

    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='cart_items')

    product = models.ForeignKey('catalog.Product',on_delete=models.CASCADE,related_name='cart_items')
    #not dynamic, what if product stock decreased ?
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def line_total(self):
        return self.product.price * self.quantity # what if price changes before checkout?

    def increase_quantity(self,amount):
        self.quantity=self.quantity+amount
        self.save()

    def decrease_quantity(self,amount):
            if self.quantity-amount<=0:
                raise ValidationError("Zero Or Negative Quantity")
            else :
                self.quantity=self.quantity-amount
                self.save()

    def save(self, *args, **kwargs):
        if self.cart.store != self.product.category.store:
            raise ValidationError("Product Doesn't Belong To Cart's Store")
        super().save(*args, **kwargs)

    def __str__(self):
        return f'item {self.product.name} in {self.cart.customer.user.username}\'s cart'

    class Meta:

        constraints = [models.UniqueConstraint(fields=['cart','product'],name='unique_product_per_customer_cart')]
        ordering = ['-added_at']