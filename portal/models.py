from django.db import models
from django.core.validators import MinValueValidator



class Plan(models.Model):

    name = models.CharField(max_length=30,unique=True)

    price = models.DecimalField(max_digits=11,decimal_places=2,validators=[MinValueValidator(0)])

    max_products = models.IntegerField(null=True,blank=True)

    max_employees = models.IntegerField(null=True,blank=True)

    allows_custom_theme = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name