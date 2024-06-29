from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Storage, User
from .forms import UserRegistrationForm, UserLoginForm, CartForm, OrderForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def cart_view(request):
    cart_form = CartForm()
    order_form = OrderForm()

    if request.method == 'POST':
        cart_form = CartForm(request.POST)
        order_form = OrderForm(request.POST)

        if cart_form.is_valid() and order_form.is_valid():
            product = cart_form.cleaned_data['product']
            quantity = cart_form.cleaned_data['quantity']
            order_type = order_form.cleaned_data['order_type']

            order_valid, message = Order.get_order(
                user=request.user,
                products=[(product.id, quantity)],
                order_type=order_type
            )

            if not order_valid:
                return render(request, 'cart.html', {
                    'cart_form': cart_form,
                    'order_form': order_form,
                    'error': message
                })

            return render(request, 'order_success.html', {'message': message})

    return render(request, 'cart.html', {
        'cart_form': cart_form,
        'order_form': order_form
    })