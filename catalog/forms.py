from django import forms
from .models import Category,Product,Review,ProductImage

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description']


class ProductForm(forms.ModelForm):

    def __init__(self,*args,store=None,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['category'].queryset = Category.objects.filter(store=store)

    class Meta:
        model = Product
        fields = ['name','category','thumbnail','description','price','stock']
        widgets = {
            'stock': forms.NumberInput(attrs={'min': 0}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating','comment']


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']