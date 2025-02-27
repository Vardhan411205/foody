from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import user_views

app_name = 'joo'  # Single namespace for all URLs

urlpatterns = [
    # Authentication URLs
    path('', user_views.home, name='home'),  # Root URL
    path('signup/', user_views.signup, name='signup'),
    path('login/', user_views.login_view, name='login'),
    path('logout/', user_views.logout_view, name='logout'),
    path('home/index/', user_views.home_page, name='home_page'),
    
    # Password Reset URLs
    path('forgot-password/', user_views.forgot_password, name='forgot_password'),
    path('reset-password/', user_views.reset_password, name='reset_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('send-reset-otp/', user_views.send_reset_otp, name='send_reset_otp'),
    path('verify-reset-otp/', user_views.verify_reset_otp, name='verify_reset_otp'),
    
    # Profile URLs
    path('profile/', include([
        path('edit/', user_views.edit_profile, name='edit_profile'),
        path('orders/', user_views.my_orders, name='my_orders'),
        path('favorites/', user_views.favorites, name='favorites'),
        path('addresses/', user_views.addresses, name='addresses'),
    ])),
    
    # Location URL
    path('update-location/', user_views.update_location, name='update_location'),
    
    # Terms and Conditions
    path('terms-conditions/', user_views.terms_conditions, name='terms_conditions'),
    
    # Partner URLs
    path('partner/', views.partner, name='partner'),
    path('partner/login/delivery/', views.delivery_login, name='delivery_login'),
    path('partner/login/restaurant/', views.restaurant_login, name='restaurant_login'),
    path('partner/login/venue/', views.venue_login, name='venue_login'),
    path('partner/register/delivery/', views.delivery, name='delivery'),
    path('partner/register/restaurant/', views.restaurant, name='restaurant'),
    path('partner/register/venue/', views.venue, name='venue'),
    path('partner/forgot-password/', views.forgot_password, name='forgot_password'),
    path('partner/verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('partner/reset-password/', views.reset_password, name='reset_password'),
    path('partner/register/delivery/submit/', views.register_delivery_partner, name='register_delivery_partner'),
    path('partner/register/restaurant/submit/', views.register_restaurant_partner, name='register_restaurant_partner'),
    path('partner/register/venue/submit/', views.register_venue_partner, name='register_venue_partner'),
    path('partner/restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('partner/venue/dashboard/', views.venue_dashboard, name='venue_dashboard'),
    path('partner/delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('partner/restaurant/logout/', views.restaurant_logout, name='restaurant_logout'),
    path('partner/restaurant/edit-profile/', views.update_restaurant_profile, name='update_restaurant_profile'),
    path('partner/restaurant/food-items/', views.restaurant_food_items, name='restaurant_food_items'),
    path('partner/restaurant/dining-tables/', views.restaurant_dining_tables, name='restaurant_dining_tables'),
    path('partner/restaurant/booking-history/', views.restaurant_booking_history, name='restaurant_booking_history'),
    path('partner/restaurant/update-booking-status/', views.update_booking_status, name='update_booking_status'),
    path('partner/venue/edit-profile/', views.venue_edit_profile, name='venue_edit_profile'),
    path('partner/venue/packages/', views.venue_packages, name='venue_packages'),
    path('partner/venue/events/', views.venue_events, name='venue_events'),
    path('partner/venue/update-event-status/', views.update_event_status, name='update_event_status'),
    path('partner/venue/bookings/', views.venue_bookings, name='venue_bookings'),
    path('partner/venue/logout/', views.venue_logout, name='venue_logout'),

    # Service URLs
    path('food/', user_views.food_view, name='food'),
    path('quickbite/', user_views.quickbite_view, name='quickbite'),
    path('dinespot/', user_views.dinespot_view, name='dinespot'),
    path('buzzfest/', user_views.buzzfest_view, name='buzzfest'),
    path('packages/', user_views.packages_view, name='packages'),
    path('payments/', user_views.payments_view, name='payments'),
    path('cart/', user_views.cart_view, name='cart'),
    path('profile/update-address/', user_views.update_address, name='update_address'),
    path('profile/delete-address/', user_views.delete_address, name='delete_address'),
    path('profile/get-address/', user_views.get_address, name='get_address'),
    path('delivery/edit-profile/', views.delivery_edit_profile, name='delivery_edit_profile'),
    path('delivery/logout/', views.delivery_logout, name='delivery_logout'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)