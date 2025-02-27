import random
import hashlib
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    DeliveryPartner, 
    RestaurantPartner, 
    VenuePartner, 
    PasswordResetOTP
)
from django.utils import timezone
from datetime import timedelta

class ForgotPasswordHandler:
    @staticmethod
    def check_email_exists(email, partner_type):
        try:
            exists = False
            if partner_type == 'delivery':
                exists = DeliveryPartner.objects.filter(email=email).exists()
                print(f"Checking delivery partner: {email}, exists: {exists}")
            elif partner_type == 'restaurant':
                exists = RestaurantPartner.objects.filter(email=email).exists()
                print(f"Checking restaurant partner: {email}, exists: {exists}")
            elif partner_type == 'venue':
                exists = VenuePartner.objects.filter(email=email).exists()
                print(f"Checking venue partner: {email}, exists: {exists}")
            
            if exists:
                print(f"Email {email} found for {partner_type} partner")
                return True
            else:
                print(f"Email {email} not found for {partner_type} partner")
                return False
            
        except Exception as e:
            print(f"Error checking email: {str(e)}")
            return False

    @staticmethod
    def generate_otp():
        return str(random.randint(1000, 9999))  # 4 digit OTP

    @staticmethod
    def send_reset_otp(email, partner_type):
        try:
            # First verify the email exists
            if not ForgotPasswordHandler.check_email_exists(email, partner_type):
                print(f"Email {email} not found for {partner_type} partner")
                return False

            # Generate OTP
            otp = ForgotPasswordHandler.generate_otp()
            print(f"Generated OTP: {otp} for {email}")

            # Delete any existing unverified OTPs for this email and partner type
            PasswordResetOTP.objects.filter(
                email=email,
                partner_type=partner_type,
                is_verified=False
            ).delete()

            # Save new OTP
            PasswordResetOTP.objects.create(
                email=email,
                otp=otp,
                partner_type=partner_type
            )
            print(f"OTP saved to database for {email}")

            # Send email
            subject = 'Password Reset OTP - Mr.Foody & Ms.Foody'
            message = f'''Hello Partner,

Your OTP for password reset is: {otp}

This OTP will expire in 30 minutes.

If you didn't request this password reset, please ignore this email.

Best regards,
Mr.Foody & Ms.Foody Team'''
            
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            print(f"OTP email sent successfully to {email}")
            return True

        except Exception as e:
            print(f"Error in send_reset_otp: {str(e)}")
            return False

    @staticmethod
    def verify_reset_otp(email, otp, partner_type):
        try:
            print(f"Verifying OTP for {email}: {otp}")
            otp_obj = PasswordResetOTP.objects.filter(
                email=email,
                partner_type=partner_type,
                is_verified=False,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).latest()

            if otp_obj and otp_obj.otp == otp:
                otp_obj.is_verified = True
                otp_obj.save()
                print(f"OTP verified successfully for {email}")
                return True
            print(f"Invalid OTP for {email}")
            return False
        except PasswordResetOTP.DoesNotExist:
            print(f"No valid OTP found for {email}")
            return False
        except Exception as e:
            print(f"Error verifying OTP: {str(e)}")
            return False

    @staticmethod
    def reset_password(email, partner_type, new_password):
        try:
            # Check if OTP was verified
            otp_verified = PasswordResetOTP.objects.filter(
                email=email,
                partner_type=partner_type,
                is_verified=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).exists()

            if not otp_verified:
                print(f"No verified OTP found for {email}")
                return False

            # Hash new password
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

            # Update password based on partner type
            if partner_type == 'delivery':
                partner = DeliveryPartner.objects.get(email=email)
            elif partner_type == 'restaurant':
                partner = RestaurantPartner.objects.get(email=email)
            elif partner_type == 'venue':
                partner = VenuePartner.objects.get(email=email)
            else:
                print(f"Invalid partner type: {partner_type}")
                return False

            partner.password = hashed_password
            partner.save()
            print(f"Password reset successful for {email}")
            return True

        except Exception as e:
            print(f"Error resetting password: {str(e)}")
            return False 