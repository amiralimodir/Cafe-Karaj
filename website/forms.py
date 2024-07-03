from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Product, Order, User, Cart
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=True)
    phone_number = forms.CharField(max_length=15, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'full_name', 'phone_number', 'password1', 'password2')


class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(label='Username or Email')
    password = forms.CharField(widget=forms.PasswordInput)


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.HiddenInput()
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_type']
        labels = {
            'order_type': 'Order Type'
        }


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sugar', 'coffee', 'flour', 'egg', 'milk', 'chocolate', 'vertical_type', 'price', 'image']


class UpdateStorageForm(forms.Form):
    ingredient_name = forms.CharField(max_length=255)
    quantity = forms.IntegerField()

class ProductFilterForm(forms.Form):
    verticals = forms.MultipleChoiceField(
        choices=Product.VERTICAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )