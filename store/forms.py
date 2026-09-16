from django import forms
from .models import Store,StoreConfig

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name','description','contact_phone','contact_email']


class StoreConfigForm(forms.ModelForm):
    class Meta:
        model = StoreConfig
        fields = ['color_pattern','theme','font','logo','banner']
        # no need for radio widget