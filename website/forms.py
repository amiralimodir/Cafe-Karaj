from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, Order, User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255)
    phone_number = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone_number', 'password']

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)

class CartForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), label='Product')
    quantity = forms.IntegerField(min_value=1, required=True, label='Quantity')

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_type']
        labels = {
            'order_type': 'Order Type'
        }


class AddProductForm(forms.Form):
    name = forms.CharField(max_length=255)
    sugar = forms.IntegerField()
    coffee = forms.IntegerField()
    flour = forms.IntegerField()
    chocolate = forms.IntegerField()
    vertical = forms.BooleanField()
    price = forms.IntegerField()

class UpdateStorageForm(forms.Form):
    ingredient_name = forms.CharField(max_length=255)
    quantity = forms.IntegerField()

class ProductFilterForm(forms.Form):
    CATEGORY_CHOICES = [
        ('cold_drink', 'Cold Drink'),
        ('hot_drink', 'Hot Drink'),
        ('cake', 'Cake'),
        ('shake', 'Shake'),
    ]
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False, label='Category')