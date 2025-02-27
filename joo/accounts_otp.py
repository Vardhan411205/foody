from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
from .models import AccountOTP

def generate_otp():
    """Generate a 4-digit OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

def send_otp(email, purpose='signup'):
    """Send OTP to email"""
    try:
        # Delete any existing unverified OTPs for this email and purpose
        AccountOTP.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=False
        ).delete()
        
        # Generate new 4-digit OTP
        otp = generate_otp()
        
        # Save OTP to database
        AccountOTP.objects.create(
            email=email,
            otp=otp,
            purpose=purpose
        )
        
        # Send email with improved formatting
        subject = 'Your Verification Code'
        message = f"""
Your verification code is: {otp}

This code will expire in 10 minutes.
Please do not share this code with anyone.
"""
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )
        
        return {
            'status': 'success',
            'message': 'OTP sent successfully'
        }
        
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        return {
            'status': 'error',
            'message': f'Failed to send OTP: {str(e)}'
        }

def verify_otp(email, otp, purpose='signup'):
    """Verify OTP"""
    try:
        # Get the latest unverified OTP for this email and purpose
        otp_obj = AccountOTP.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=False
        ).latest('created_at')
        
        # Check if OTP is expired (10 minutes)
        time_diff = timezone.now() - otp_obj.created_at
        if time_diff > timedelta(minutes=10):
            return {
                'status': 'error',
                'message': 'OTP has expired. Please request a new one.'
            }
        
        # Verify OTP
        if otp_obj.otp == otp:
            otp_obj.is_verified = True
            otp_obj.save()
            return {
                'status': 'success',
                'message': 'OTP verified successfully'
            }
        else:
            return {
                'status': 'error',
                'message': 'Invalid OTP'
            }
            
    except AccountOTP.DoesNotExist:
        return {
            'status': 'error',
            'message': 'OTP not found. Please request a new one.'
        }
    except Exception as e:
        print(f"Error verifying OTP: {str(e)}")
        return {
            'status': 'error',
            'message': f'Failed to verify OTP: {str(e)}'
        }

def is_email_verified(email, purpose='signup'):
    """Check if email is verified"""
    try:
        return AccountOTP.objects.filter(
            email=email,
            purpose=purpose,
            is_verified=True
        ).exists()
    except Exception:
        return False 