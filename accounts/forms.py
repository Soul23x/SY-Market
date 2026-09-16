from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User,Address,Employee



class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email','phone_number','first_name','last_name')

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name'].strip()
        if not first_name:
            raise forms.ValidationError('First name is required.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name'].strip()
        if not last_name:
            raise forms.ValidationError('Last name is required.')
        return last_name



class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','phone_number']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['governorate','city','street','building','unit','notes']


class EmployeeAddForm(forms.ModelForm):

    email = forms.EmailField()

    class Meta:
        model = Employee
        fields = ['permissions']

    # custom clean method, runs on is_valid()
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No User Found With This Email')
        if hasattr(User.objects.filter(email=email).first(),'store_owner'): # new
            raise forms.ValidationError('Invalid Email')
        return email



class EmployeeEditForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ['permissions']