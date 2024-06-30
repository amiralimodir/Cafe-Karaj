from django.urls import path
from .views import register, login_view, cart_view

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('cart/', cart_view, name='cart'),

]
