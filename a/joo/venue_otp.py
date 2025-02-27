import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTPVerification
from django.utils import timezone
from datetime import timedelta
import hashlib

class VenueOTPHandler:
    @staticmethod
    def generate_otp():
        return str(random.randint(1000, 9999))  # 4 digit OTP

    @staticmethod
    def send_otp(email):
        try:
            # Generate OTP
            otp = VenueOTPHandler.generate_otp()
            
            # Delete any existing unverified OTPs for this email
            OTPVerification.objects.filter(
                email=email,
                partner_type='venue',
                is_verified=False
            ).delete()

            # Save OTP to database
            OTPVerification.objects.create(
                email=email,
                otp=otp,
                partner_type='venue'
            )

            # Send email
            subject = 'Venue Registration OTP - Mr.Foody & Ms.Foody'
            message = f'''Hello Venue Partner,

Your OTP for registration is: {otp}

This OTP will expire in 30 minutes.

Best regards,
Mr.Foody & Ms.Foody Team'''
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            print(f"Error sending OTP: {str(e)}")
            return False

    @staticmethod
    def verify_otp(email, otp):
        try:
            otp_obj = OTPVerification.objects.filter(
                email=email,
                partner_type='venue',
                is_verified=False,
                created_at__gte=timezone.now() - timedelta(minutes=30)
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