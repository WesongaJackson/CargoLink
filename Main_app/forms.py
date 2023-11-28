from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile, Vehicle
from  django.contrib.auth.forms import  UserCreationForm


# registration form
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username','first_name','last_name','email','password1','password2']
        labels = {

            "email": "Email Address"
        }





# loginform
class LoginForm(forms.Form):
    username = forms.CharField(max_length=10)
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['location', 'phone_number', 'image', 'owner']

        def clean_phone_number(self):
            phone_number = self.cleaned_data.get('phone_number')
            if User.objects.filter(phone_number=phone_number).exists():
                raise ValidationError("This phone number is already inuse")
            return phone_number


# vehicle listing form
class SelectWithEmptyOptionMixin:
    def add_select_with_empty_option(self, field_name):
        choices = self.fields[field_name].choices
        if choices and choices[0][0] == '':
            choices = choices[1:]
        self.fields[field_name].choices = [('', '-----select----')] + choices


class ListForm(SelectWithEmptyOptionMixin, forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['image', 'model', 'type', 'location', 'for_hire_or_sell', 'price']
        widgets = {

            "price": forms.NumberInput(attrs={"max": 2000000, "min": 500, "class": "w-100"})
        }
        labels = {

            "for_hire_or_sell": "For Hire/Sell"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('model', 'type', 'for_hire_or_sell'):
            self.add_select_with_empty_option(field_name)


# searchform
class SearchForm(SelectWithEmptyOptionMixin, forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['model', 'type', 'location', 'for_hire_or_sell', 'price']
        widgets = {

            "price": forms.NumberInput(attrs={"max": 5000000, "min": 500, "class": "w-100"}),

        }
        labels = {
            "for_hire_or_sell": "For Hire/Sell",
            "price": "Your Budget"
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ('model', 'type', 'for_hire_or_sell'):
            self.fields[field_name].required = False
            self.add_select_with_empty_option(field_name)
        self.fields['location'].required = False
        self.fields['price'].required = False
