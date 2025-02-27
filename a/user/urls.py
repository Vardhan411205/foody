from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # Main pages
    path('food/', views.food, name='food'),
    path('dinespot/', views.dinespot, name='dinespot'),
    path('quickbite/', views.quickbite, name='quickbite'),
    path('buzzfest/', views.buzzfest, name='buzzfest'),
    path('packages/', views.packages, name='packages'),
    
    # Profile pages
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/orders/', views.my_orders, name='my_orders'),
    path('profile/favorites/', views.favorites, name='favorites'),
    path('profile/addresses/', views.addresses, name='addresses'),
    
    # Cart and Payment pages
    path('cart/', views.cart, name='cart'),
    path('payments/', views.payments, name='payments'),
] 