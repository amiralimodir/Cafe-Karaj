from django.urls import path
from .views import register, user_login, cart_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('cart/', cart_view, name='cart'),

]
