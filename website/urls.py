from django.urls import path
from .views import register, user_login, cart_view, product_list,update_storage_view,add_product_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('cart/', cart_view, name='cart'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('update_storage/', views.update_storage_view, name='update_storage'),
    path('products/', views.product_list_view, name='product_list')

]

