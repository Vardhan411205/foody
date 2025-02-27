from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import AccountOTP, OTPVerification
import random

def generate_otp():
    """Generate a 4-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

def send_otp(email, partner_type):
    """Send OTP email for various purposes"""
    try:
        # Generate OTP
        otp = generate_otp()
        
        # Save OTP to appropriate table based on partner_type
        if partner_type in ['delivery', 'restaurant', 'venue']:
            # For partner registrations
            OTPVerification.objects.create(
                email=email,
                otp=otp,
                partner_type=partner_type,
                is_verified=False,
                created_at=timezone.now()
            )
        else:
            # For user signup and password reset
            AccountOTP.objects.create(
                email=email,
                otp=otp,
                purpose=partner_type,
                is_verified=False
            )
        
        # Customize email subject based on partner_type
        subjects = {
            'signup': 'Email Verification - Mr.Foody & Ms.Foody',
            'venue': 'Venue Partner Registration - Mr.Foody & Ms.Foody',
            'delivery': 'Delivery Partner Registration - Mr.Foody & Ms.Foody',
            'restaurant': 'Restaurant Partner Registration - Mr.Foody & Ms.Foody',
            'reset': 'Password Reset - Mr.Foody & Ms.Foody'
        }
        
        subject = subjects.get(partner_type, 'Email Verification - Mr.Foody & Ms.Foody')
        
        # Email message
        message = f'''Hello,

Your verification code is: {otp}

This code will expire in 10 minutes.
Please do not share this code with anyone.

Best regards,
Mr.Foody & Ms.Foody Team'''
        
        # Send email
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        print(f"OTP sent successfully to {email} for {partner_type}")  # Debug log
        return {'status': 'success', 'message': 'OTP sent successfully'}
        
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")  # Debug log
        return {'status': 'error', 'message': str(e)}

def verify_otp(email, otp, partner_type):
    """Verify OTP for various purposes"""
    try:
        if partner_type in ['delivery', 'restaurant', 'venue']:
            # For partner verifications
            otp_record = OTPVerification.objects.filter(
                email=email,
                partner_type=partner_type,
                is_verified=False,
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).latest('created_at')
        else:
            # For user verifications
            otp_record = AccountOTP.objects.filter(
                email=email,
                purpose=partner_type,
                is_verified=False,
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).latest('created_at')
        
        if otp_record.otp == otp:
            otp_record.is_verified = True
            otp_record.save()
            print(f"OTP verified successfully for {email}")  # Debug log
            return {'status': 'success', 'message': 'OTP verified successfully'}
        else:
            return {'status': 'error', 'message': 'Invalid OTP'}
            
    except (OTPVerification.DoesNotExist, AccountOTP.DoesNotExist):
        return {'status': 'error', 'message': 'OTP expired or not found'}
    except Exception as e:
        print(f"Error verifying OTP: {str(e)}")  # Debug log
        return {'status': 'error', 'message': str(e)}

# Keep these for backward compatibility
def send_signup_otp(email):
    return send_otp(email, 'signup')

def verify_signup_otp(email, otp):
    return verify_otp(email, otp, 'signup') 