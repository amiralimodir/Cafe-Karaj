from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.utils.functional import SimpleLazyObject
from .models import Product, Order, Storage, OrderProduct,UserOrder, User,Cart
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

User = get_user_model()

@login_required
def product_list_view(request):
    products = Product.objects.all()
    filter_form = ProductFilterForm(request.GET)
    cart_form = CartForm()

    if filter_form.is_valid():
        vertical_type = filter_form.cleaned_data.get('vertical_type')
        if vertical_type:
            products = products.filter(vertical_type__in=vertical_type)

    if request.method == 'POST':
        cart_form = CartForm(request.POST)
        if cart_form.is_valid():
            cart_item = cart_form.save(commit=False)

            username = request.user.username
            cart_item.username = username

            existing_cart_item = Cart.objects.filter(username=username, product=cart_item.product).first()
            if existing_cart_item:
                existing_cart_item.quantity += cart_item.quantity
                existing_cart_item.save()
            else:
                cart_item.save()

            return redirect('product_list')

    context = {
        'products': products,
        'filter_form': filter_form,
        'cart_form': cart_form
    }
    return render(request, 'product_list.html', context)

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(username=request.user.username)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        cart_id = request.POST.get('cart_id')
        quantity = request.POST.get('quantity')
        cart_item = get_object_or_404(Cart, id=cart_id)
        cart_item.quantity = int(quantity)
        cart_item.save()
        return redirect('cart')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

@login_required
def place_order(request):
    cart_items = Cart.objects.filter(username=request.user.username)
    if request.method == 'POST':
        order_type = request.POST.get('order_type') == 'on'
        products = [(item.product.id, item.quantity) for item in cart_items]
        
        success, message = Order.get_order(request.user, products, order_type)
        
        if success:
            cart_items.delete()
            return redirect('order_success')
        else:
            return render(request, 'cart.html', {'error': message, 'cart_items': cart_items})
    
    return redirect('cart')


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
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            Product.add_product(
                name=data['name'],
                sugar=data['sugar'],
                coffee=data['coffee'],
                flour=data['flour'],
                egg=data['egg'],
                milk=data['milk'],
                chocolate=data['chocolate'],
                vertical_type=data['vertical_type'],
                price=data['price'],
                image=data['image']
            )
            return redirect('product_list')
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
                return redirect('management_dashboard')
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