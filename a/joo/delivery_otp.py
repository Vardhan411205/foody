import random
import hashlib
from django.core.mail import send_mail
from django.conf import settings
from .models import OTPVerification
from django.utils import timezone
from datetime import timedelta

class DeliveryOTPHandler:
    @staticmethod
    def generate_otp():
        return str(random.randint(1000, 9999))  # 4 digit OTP

    @staticmethod
    def send_otp_email(email, otp):
        subject = 'OTP Verification - Mr.Foody & Ms.Foody Delivery Partner'
        message = f'Your OTP for email verification is: {otp}\n\nThis OTP will expire in 30 minutes.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )

    @staticmethod
    def verify_otp(email, otp):
        try:
            otp_obj = OTPVerification.objects.filter(
                email=email,
                partner_type='delivery',
                is_verified=False,
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).latest()

            if otp_obj and otp_obj.otp == otp:
                otp_obj.is_verified = True
                otp_obj.save()
                return True
            return False
        except OTPVerification.DoesNotExist:
            return False

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest() 