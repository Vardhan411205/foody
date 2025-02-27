from django.urls import path
from . import user_views

app_name = 'joo'

urlpatterns = [
    path('signup/', user_views.signup, name='signup'),
    path('login/', user_views.login_view, name='login'),
    path('logout/', user_views.logout_view, name='logout'),
    path('home/index/', user_views.home_page, name='home_page'),
    path('forgot-password/', user_views.forgot_password, name='forgot_password'),
    path('reset-password/', user_views.reset_password, name='reset_password'),
    path('verify-otp/', user_views.verify_otp, name='verify_otp'),
    path('send-otp/', user_views.send_otp, name='send_otp'),
    path('terms-conditions/', user_views.terms_conditions, name='terms_conditions'),
    path('send-reset-otp/', user_views.send_reset_otp, name='send_reset_otp'),
    path('verify-reset-otp/', user_views.verify_reset_otp, name='verify_reset_otp'),
    path('partner/', user_views.partner, name='partner'),
] 