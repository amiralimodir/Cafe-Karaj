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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'sugar': forms.NumberInput(attrs={'class': 'form-control'}),
            'coffee': forms.NumberInput(attrs={'class': 'form-control'}),
            'flour': forms.NumberInput(attrs={'class': 'form-control'}),
            'egg': forms.NumberInput(attrs={'class': 'form-control'}),
            'milk': forms.NumberInput(attrs={'class': 'form-control'}),
            'chocolate': forms.NumberInput(attrs={'class': 'form-control'}),
            'vertical_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'نام',
            'sugar': 'شکر',
            'coffee': 'قهوه',
            'flour': 'آرد',
            'egg': 'تخم مرغ',
            'milk': 'شیر',
            'chocolate': 'شکلات',
            'vertical_type': 'نوع دسته بندی',
            'vertical_type': 'نوع دسته بندی',
            'price': 'قیمت',
            'image': 'تصویر',
        }

    def __init__(self, *args, **kwargs):
        super(AddProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.label_suffix = ''
class UpdateStorageForm(forms.Form):
    ingredient_name = forms.CharField(max_length=255)
    quantity = forms.IntegerField()

class ProductFilterForm(forms.Form):
    verticals = forms.MultipleChoiceField(
        choices=Product.VERTICAL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )