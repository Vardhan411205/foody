from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
import random
import json
from decimal import Decimal, InvalidOperation
from datetime import date

from .models import User, AccountOTP, ResetPasswordOTP, Address

def home(request):
    """Redirect to signup page"""
    return redirect('joo:signup')

@csrf_exempt
def signup(request):
    """Handle user signup"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            full_name = data.get('full_name')
            phone = data.get('phone')
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'Email already exists'})
            
            # Create user with full name
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )
            
            # Split full name into first and last name
            names = full_name.split(' ', 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ''
            
            # Add phone number if your User model has this field
            if hasattr(user, 'phone'):
                user.phone = phone
                
            user.save()
            
            return JsonResponse({'status': 'success', 'message': 'Account created successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return render(request, 'user/signup.html')

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'success', 'redirect_url': '/home/index/'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return render(request, 'user/login.html')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('joo:login')

@login_required
def home_page(request):
    """Render home page for logged in users"""
    return render(request, 'home/index.html')

def forgot_password(request):
    """Render forgot password page"""
    return render(request, 'user/forgot_password.html')

@csrf_exempt
def reset_password(request):
    """Handle password reset"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            password = data.get('password')
            email = request.session.get('reset_email')
            
            if not email:
                return JsonResponse({
                'status': 'error',
                    'message': 'Reset session expired. Please try again from forgot password.'
                })
            
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                
                request.session.pop('reset_email', None)
                ResetPasswordOTP.objects.filter(email=email).delete()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Password reset successful'
                })
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User not found'
                })
        except Exception as e:
            print("Password reset error:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': 'Error resetting password'
            })
    return render(request, 'user/reset_password.html')

@csrf_exempt
def send_otp(request):
    """Send OTP for email verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            
            AccountOTP.objects.create(
                email=email,
                otp=otp,
                purpose='signup'
            )
            
            # HTML Email Template
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #fc8019;
                        color: white;
                        text-align: center;
                        padding: 30px 20px;
                        border-radius: 10px 10px 0 0;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-family: 'Arial', sans-serif;
                    }}
                    .content {{
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }}
                    .otp-box {{
                        background-color: #f8f8f8;
                        padding: 20px;
                        text-align: center;
                        margin: 20px 0;
                        border-radius: 5px;
                        border: 2px dashed #fc8019;
                    }}
                    .otp-code {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #fc8019;
                        letter-spacing: 5px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        color: #666;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Mr.Foody & Ms.Foody</h1>
                    </div>
                    <div class="content">
                        <h2>Verify Your Email</h2>
                        <p>Hello!</p>
                        <p>Thank you for choosing Mr.Foody & Ms.Foody. To complete your registration, please use the following OTP code:</p>
                        
                        <div class="otp-box">
                            <div class="otp-code">{otp}</div>
                            <p>This code will expire in 10 minutes</p>
                        </div>
                        
                        <p>If you didn't request this code, please ignore this email.</p>
                        
                        <div class="footer">
                            <p>This is an automated message, please do not reply.</p>
                            <p>&copy; 2024 Mr.Foody & Ms.Foody. All rights reserved.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version for email clients that don't support HTML
            plain_message = f"""
            Your OTP for Mr.Foody & Ms.Foody verification is: {otp}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            """
            
            send_mail(
                subject='Verify Your Email - Mr.Foody & Ms.Foody',
                message=plain_message,
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return JsonResponse({'status': 'success', 'message': 'OTP sent successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def verify_otp(request):
    """Verify OTP for email verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')
            
            otp_obj = AccountOTP.objects.filter(
                email=email,
                otp=otp,
                purpose='signup',
                is_verified=False
            ).first()
            
            if otp_obj:
                otp_obj.is_verified = True
                otp_obj.save()
                return JsonResponse({
                    'status': 'success',
                    'message': 'OTP verified successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid OTP'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

def terms_conditions(request):
    """Render terms and conditions page"""
    return render(request, 'user/terms_conditions.html')

@csrf_exempt
def send_reset_otp(request):
    """Send OTP for password reset"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No account found with this email'
                })
            
            # Generate OTP
            otp = ''.join(random.choices('0123456789', k=4))
            
            # Save OTP
            ResetPasswordOTP.objects.filter(email=email).delete()
            ResetPasswordOTP.objects.create(
                email=email,
                otp=otp,
                is_verified=False
            )
            
            # Send email
            subject = 'Password Reset OTP'
            message = f'Your OTP for password reset is: {otp}'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            return JsonResponse({
                'status': 'success',
                'message': 'Reset OTP sent successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def verify_reset_otp(request):
    """Verify OTP for password reset"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')
            
            otp_obj = ResetPasswordOTP.objects.filter(
                email=email,
                otp=otp,
                is_verified=False
            ).first()
            
            if otp_obj:
                otp_obj.is_verified = True
                otp_obj.save()
                request.session['reset_email'] = email
                return JsonResponse({
                    'status': 'success',
                    'message': 'OTP verified successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid OTP'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@login_required
def edit_profile(request):
    """Handle user profile editing"""
    if request.method == 'GET':
        return render(request, 'home/profile/edit-profile.html')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Update user info
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'password' in data and data['password']:
                user.set_password(data['password'])
            
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

def partner(request):
    """Handle partner page"""
    return render(request, 'user/partner.html')

@login_required
def my_orders(request):
    """Render my orders page"""
    return render(request, 'home/profile/my-orders.html')

@login_required
def favorites(request):
    """Render favorites page"""
    return render(request, 'home/profile/favorites.html')

@login_required
def addresses(request):
    """Render addresses page"""
    user = request.user
    addresses = []
    
    # Get all non-empty addresses
    if user.location1:
        addresses.append({
            'id': 'location1',
            'address': user.location1.split('[')[0].strip(),  # Remove coordinates
            'coordinates': user.location1.split('[')[1].rstrip(']') if '[' in user.location1 else None
        })
    if user.location2:
        addresses.append({
            'id': 'location2',
            'address': user.location2.split('[')[0].strip(),
            'coordinates': user.location2.split('[')[1].rstrip(']') if '[' in user.location2 else None
        })
    if user.location3:
        addresses.append({
            'id': 'location3',
            'address': user.location3.split('[')[0].strip(),
            'coordinates': user.location3.split('[')[1].rstrip(']') if '[' in user.location3 else None
        })
    if user.location4:
        addresses.append({
            'id': 'location4',
            'address': user.location4.split('[')[0].strip(),
            'coordinates': user.location4.split('[')[1].rstrip(']') if '[' in user.location4 else None
        })
    if user.location5:
        addresses.append({
            'id': 'location5',
            'address': user.location5.split('[')[0].strip(),
            'coordinates': user.location5.split('[')[1].rstrip(']') if '[' in user.location5 else None
        })
    
    return render(request, 'home/profile/addresses.html', {'addresses': addresses})

@login_required
def food(request):
    """Render food delivery page"""
    return render(request, 'home/food.html')

@login_required
def quickbite(request):
    """Render quickbite page"""
    return render(request, 'home/quickbite.html')

@login_required
def dinespot(request):
    """Render dinespot page"""
    return render(request, 'home/dinespot.html')

@login_required
def buzzfest(request):
    """Render buzzfest page"""
    context = {
        'today': date.today(),
        'venues': []  # Add your venues data here
    }
    return render(request, 'home/buzzfest.html', context)

@login_required
def packages(request):
    """Render packages page"""
    return render(request, 'home/packages.html')

@login_required
def cart(request):
    """Render cart page"""
    return render(request, 'home/cart/cart.html')

@login_required
def payments(request):
    """Render payments page"""
    return render(request, 'home/payments/payments.html')

@login_required
@csrf_exempt
def update_address(request):
    """Handle address updates"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Received data:", data)
            
            user = request.user
            address_text = data.get('address')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            
            full_address = f"{address_text} [{latitude}, {longitude}]"
            
            if not user.location1 or user.location1.strip() == '':
                user.location1 = full_address
            elif not user.location2 or user.location2.strip() == '':
                user.location2 = full_address
            elif not user.location3 or user.location3.strip() == '':
                user.location3 = full_address
            elif not user.location4 or user.location4.strip() == '':
                user.location4 = full_address
            elif not user.location5 or user.location5.strip() == '':
                user.location5 = full_address
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Maximum number of addresses (5) reached.'
                })
            
            user.save()
            
            location_id = None
            if full_address == user.location1:
                location_id = 'location1'
            elif full_address == user.location2:
                location_id = 'location2'
            elif full_address == user.location3:
                location_id = 'location3'
            elif full_address == user.location4:
                location_id = 'location4'
            elif full_address == user.location5:
                location_id = 'location5'
            
            return JsonResponse({
                'status': 'success',
                'message': 'Address saved successfully',
                'location_id': location_id,
                'address': {
                    'id': location_id,
                    'address': address_text,
                    'coordinates': f"{latitude}, {longitude}"
                }
            })
        except Exception as e:
            print("Error saving address:", str(e))
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@login_required
def delete_address(request):
    """Handle address deletion"""
    if request.method == 'DELETE':
        try:
            address_id = request.GET.get('id')
            user = request.user
            
            if not address_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Address ID is required'
                })
            
            if address_id == 'location1':
                user.location1 = ''
            elif address_id == 'location2':
                user.location2 = ''
            elif address_id == 'location3':
                user.location3 = ''
            elif address_id == 'location4':
                user.location4 = ''
            elif address_id == 'location5':
                user.location5 = ''
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid address ID'
                })
            
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Address deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@login_required
def get_address(request):
    """Get specific address"""
    address_id = request.GET.get('id')
    try:
        address = Address.objects.get(id=address_id, user=request.user)
        return JsonResponse({
                    'status': 'success',
            'address': {
                'id': address.id,
                'type': address.address_type,
                'address': address.address,
                'coordinates': {
                    'lat': float(address.latitude),
                    'lng': float(address.longitude)
                }
            }
        })
    except Address.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
            'message': 'Address not found'
        })
        