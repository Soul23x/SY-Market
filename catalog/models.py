from django.db import models
from django.core.validators import MinValueValidator , MaxValueValidator
from django.core.exceptions import ValidationError


class Category(models.Model):

    store = models.ForeignKey('store.Store',on_delete=models.CASCADE,related_name='categories')

    name = models.CharField(max_length=30)

    description = models.TextField(blank=True,null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: 
        constraints = [models.UniqueConstraint(fields=['store','name'],name='unique_category_per_store')]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):

        if self.name=='uncategorized':
            raise ValidationError("Can Not Delete Category : uncategorized")

        if Product.objects.filter(category=self):

            uncategorized, created = Category.objects.get_or_create(name='uncategorized',store=self.store,is_active=False) # no defaults here
        
            Product.objects.filter(category=self).update(category=uncategorized)

        super().delete(*args, **kwargs)
        

class Product(models.Model):

    category = models.ForeignKey(Category,on_delete=models.RESTRICT,related_name='products')

    thumbnail = models.ImageField(upload_to='product_thumbnails')

    name = models.CharField(max_length=50)

    description = models.TextField()

    price = models.DecimalField(max_digits=11,decimal_places=2,validators=[MinValueValidator(0)])

    stock = models.IntegerField(validators=[MinValueValidator(0)])

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    average_rating = models.DecimalField(max_digits=3,decimal_places=1,null=True,blank=True, validators=[MinValueValidator(0),MaxValueValidator(10)])
    
    review_count = models.IntegerField(default=0,validators=[MinValueValidator(0)])

    def __str__(self):
        return self.name


class ProductImage(models.Model):

    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='product_images')

    image = models.ImageField(upload_to='product_previews')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.product.name}'

    class Meta:
        ordering = ["-created_at"]



class Review(models.Model):

    customer = models.ForeignKey('accounts.Customer',on_delete=models.CASCADE,related_name='reviews')

    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')

    rating = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(10)])

    comment = models.TextField(null=True,blank=True)

    is_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['customer','product'],name='unique_customer_review_per_product')]        
        ordering=['-created_at']

    def __str__(self):
        return f'{self.customer.user.username} -> {self.product.name}'