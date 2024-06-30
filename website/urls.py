from django.urls import path
from .views import register, login_view , cart_view, product_list_view, update_storage_view, add_product_view, purchase_records_view, homepage_view

urlpatterns = [
    path('', homepage_view, name='homepage'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('cart/', cart_view, name='cart'),
    path('add_product/', add_product_view, name='add_product'),
    path('update_storage/', update_storage_view, name='update_storage'),
    path('products/', product_list_view, name='product_list'),
    path('purchase_records/', purchase_records_view, name='purchase_records'),
    


]