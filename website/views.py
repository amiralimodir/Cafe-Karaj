from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Order, Storage, OrderProduct,UserOrder, User
from django.http import HttpResponse
from .forms import CustomUserCreationForm, UserLoginForm, CartForm, OrderForm, ProductFilterForm, AddProductForm, UpdateStorageForm
from django.db.models import Count
from .decorators import admin_required
import datetime

def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            return redirect('login')
    else:
        user_form = CustomUserCreationForm()
    return render(request, 'register.html', {'user_form': user_form})

    
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data.get('username_or_email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username_or_email, password=password)
            if user is not None:
                login(request, user)
                if request.user.is_superuser:
                    return redirect('management_dashboard')
                else:
                    return redirect('authenticated_homepage')
            else:
                return HttpResponse("Invalid login credentials")
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('unauthenticated_homepage')

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

@login_required
def product_list_view(request):
    form = ProductFilterForm(request.GET or None)
    products = Product.objects.all()

    if form.is_valid():
        category = form.cleaned_data.get('category')
        if category:
            if category == 'cold_drink':
                products = products.filter(vertical=True)
            elif category == 'hot_drink':
                products = products.filter(vertical=False)
            elif category == 'cake':
                products = products.filter(name__icontains='cake')
            elif category == 'shake':
                products = products.filter(name__icontains='shake')

    return render(request, 'product_list.html', {'form': form, 'products': products})

def unauthenticated_homepage_view(request):
    if request.user.is_authenticated:
        return redirect('authenticated_homepage')
    return render(request, 'unauthenticated_homepage.html')

@login_required
def authenticated_homepage_view(request):


    most_sold_products = (OrderProduct.objects.values('product_id')
                          .annotate(total_sales=Count('product_id'))
                          .order_by('-total_sales')[:12])

    product_ids = [item['product_id'] for item in most_sold_products]
    products = Product.objects.filter(id__in=product_ids)

    product_sales_dict = {item['product_id']: item['total_sales'] for item in most_sold_products}

    products_with_sales = [{'product': product, 'total_sales': product_sales_dict[product.id]} for product in products]

    return render(request, 'authenticated_homepage.html', {

        'products_with_sales': products_with_sales
    })




@login_required
def purchase_records_view(request):
    user_orders = UserOrder.objects.filter(user=request.user)
    orders = []

    for user_order in user_orders:
        order = user_order.order
        order_products = OrderProduct.objects.filter(order=order)
        products = [{'product': order_product.product, 'quantity': 1} for order_product in order_products]

        orders.append({
            'order_id': order.id,
            'purchase_amount': order.purchase_amount,
            'type': 'take away' if order.type == b'\x01' else 'dine in',
            'products': products,
            'order_date': order.created_at
        })

    return render(request, 'purchase_records.html', {'orders': orders})

@login_required
@admin_required
def add_product_view(request):
    if request.method == 'POST':
        form = AddProductForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Product.add_product(
                name=data['name'],
                sugar=data['sugar'],
                coffee=data['coffee'],
                flour=data['flour'],
                chocolate=data['chocolate'],
                vertical=data['vertical'],
                price=data['price']
            )
            return redirect('products')  
    else:
        form = AddProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required
@admin_required
def update_storage_view(request):
    if request.method == 'POST':
        form = UpdateStorageForm(request.POST)
        if form.is_valid():
            ingredient_name = form.cleaned_data['ingredient_name']
            quantity = form.cleaned_data['quantity']
            result = Storage.update_storage(ingredient_name, quantity)
            if result['status'] == 'success':
                return redirect('storage_list')  # Replace with the name of your storage list view
            else:
                form.add_error(None, result['message'])
    else:
        form = UpdateStorageForm()
    return render(request, 'update_storage.html', {'form': form})



@login_required
@admin_required
def management_dashboard_view(request):

    sales_data = (
        OrderProduct.objects.values('product__name')
        .annotate(sales_count=Count('product'))
        .order_by('-sales_count')[:10]
    )

    products = Product.objects.all()
    sales_chart_data = {
        'labels': [data['product__name'] for data in sales_data],
        'data': [data['sales_count'] for data in sales_data],
    }

    context = {
        'products': products,
        'sales_chart_data': sales_chart_data,
    }
    return render(request, 'management_dashboard.html', context)