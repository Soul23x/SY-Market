from django.db import models

class Store(models.Model):

    owner = models.OneToOneField('accounts.StoreOwner',on_delete=models.PROTECT,related_name='store')

    name = models.CharField(max_length=30)

    subdomain = models.CharField(max_length=50,unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)

    description = models.TextField(blank=True,null=True)
    
    contact_phone = models.CharField(max_length=15,blank=True,null=True)
    
    contact_email = models.EmailField(blank=True,null=True)

    def __str__(self):
        return self.name



class Colors(models.TextChoices):

    RED = "RED","Red"

    YELLOW = "YELLOW","Yellow"

    ORANGE = "ORANGE","Orange"

    BLUE = "BLUE","Blue"

    TEAL = "TEAL","Teal"

    PURPLE = "PURPLE","Purple"

    PINK = "PINK","Pink"

    GREEN = "GREEN","Green"

    LIME = "LIME","Lime"



class Theme(models.TextChoices):

    DARK = "DARK","Dark"

    LIGHT = "LIGHT","Light"


class Font(models.TextChoices):

    ARIAL = "ARIAL","Arial"

    TAHOMA = "TAHOMA","Tahoma"

    HELVETICA = "HELVETICA","Helvetica"



class StoreConfig(models.Model):

    store = models.OneToOneField(Store,on_delete=models.CASCADE,related_name='config') 

    color_pattern = models.CharField(max_length=15,choices=Colors.choices)

    theme = models.CharField(max_length=30,choices=Theme.choices)

    font = models.CharField(max_length=30,choices=Font.choices)

    logo = models.ImageField(upload_to='store_logos',blank=True,null=True)

    banner = models.ImageField(upload_to='store_banners',blank=True,null=True)

    def __str__(self):
        return f'Config for {self.store.name}'