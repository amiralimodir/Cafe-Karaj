from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import Product, Order, Storage, User, Admin, OrderProduct,UserOrder
from .forms import UserRegistrationForm, UserLoginForm, CartForm, OrderForm, ProductFilterForm
from django.db.models import Count

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

def homepage_view(request):
    is_admin = request.user.is_authenticated and Admin.objects.filter(username=request.user.username).exists()

    most_sold_products = (OrderProduct.objects.values('product_id')
                          .annotate(total_sales=Count('product_id'))
                          .order_by('-total_sales')[:12])

    product_ids = [item['product_id'] for item in most_sold_products]
    products = Product.objects.filter(id__in=product_ids)

    product_sales_dict = {item['product_id']: item['total_sales'] for item in most_sold_products}

    products_with_sales = [{'product': product, 'total_sales': product_sales_dict[product.id]} for product in products]

    return render(request, 'homepage.html', {'is_admin': is_admin, 'products_with_sales': products_with_sales})


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