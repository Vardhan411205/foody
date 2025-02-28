from django.urls import path
from . import views

app_name = 'joo'

urlpatterns = [
    # Authentication URLs
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/index/', views.home_page, name='home_page'),
    
    # Main service URLs
    path('food/', views.food, name='food'),
    path('quickbite/', views.quickbite, name='quickbite'),
    path('dinespot/', views.dinespot, name='dinespot'),
    path('buzzfest/', views.buzzfest, name='buzzfest'),
    path('packages/', views.packages, name='packages'),
    
    # Cart and Payment URLs
    path('cart/', views.cart, name='cart'),
    path('payments/', views.payments, name='payments'),
    
    # Profile URLs
    path('my-orders/', views.my_orders, name='my_orders'),
    path('favorites/', views.favorites, name='favorites'),
    path('addresses/', views.addresses, name='addresses'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Other URLs
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('partner/', views.partner, name='partner'),
    
    # Password Reset URLs
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('send-reset-otp/', views.send_reset_otp, name='send-reset-otp'),
    path('verify-reset-otp/', views.verify_reset_otp, name='verify-reset-otp'),
    
    # OTP Verification URLs
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('send-otp/', views.send_otp, name='send_otp'),
    
    # Add this URL pattern
    path('update-address/', views.update_address, name='update_address'),
    path('delete-address/', views.delete_address, name='delete_address'),
    path('get-address/', views.get_address, name='get_address'),
]