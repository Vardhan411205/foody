from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login, authenticate, logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import AccountOTP, ResetPasswordOTP, FoodItem, DiningTable
import json
import random
from django.contrib.auth.hashers import make_password
from .accounts_otp import send_otp, verify_otp, is_email_verified
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .user_data import UserData
from django.contrib import messages

User = get_user_model()  # This will get your custom User model

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(4)])

def home(request):
    """Redirect root URL to signup page"""
    return redirect('joo:signup')

def signup(request):
    """
    Handle user signup and display signup page
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            full_name = data.get('full_name')
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already registered'
                })
            
            if not is_email_verified(email, 'signup'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })
            
            first_name = full_name.split()[0]
            last_name = ' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
            
            # Create user and profile
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Account created successfully! Please login.',
                'redirect_url': reverse('joo:login')
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return render(request, 'user/signup.html')

def redirect_to_login(request):
    """Redirect root URL to login page"""
    return redirect('joo:login')

@login_required
def home_page(request):
    """Display user home page"""
    try:
        user = User.objects.get(id=request.user.id)
        
        # Ensure session data is up to date
        request.session['user_name'] = user.get_full_name() or user.email
        request.session['user_email'] = user.email
        request.session['user_first_name'] = user.first_name
        request.session['user_last_name'] = user.last_name
        
        # Safely get location with fallback
        try:
            current_location = user.current_location
        except AttributeError:
            current_location = 'Select your location'
            
        request.session['user_location'] = current_location
        
        return render(request, 'home/index.html')
    except User.DoesNotExist:
        logout(request)
        return redirect('joo:login')

def logout_view(request):
    """Handle user logout"""
    # Clear all session data
    request.session.flush()
    logout(request)
    return redirect('joo:login')

def terms_conditions(request):
    return render(request, 'user/terms_conditions.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember') == 'on'
        
        user = authenticate(username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Store user data in session
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            request.session['user_name'] = user.get_full_name() or user.email
            request.session['user_first_name'] = user.first_name
            request.session['user_last_name'] = user.last_name
            
            # Safely get location with fallback
            try:
                current_location = user.current_location
            except AttributeError:
                current_location = 'Select your location'
            
            request.session['user_location'] = current_location
            
            # Set session expiry
            if remember:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)
            
            return redirect('joo:home_page')
        else:
            return render(request, 'user/login.html', {
                'error': 'Invalid email or password'
            })
    
    return render(request, 'user/login.html')

@csrf_exempt
def send_user_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            if not email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email is required'
                })
            
            # Use the new function directly
            result = send_otp(email, 'user')
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

@csrf_exempt
def verify_user_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')
            
            # Use the new function directly
            result = verify_otp(email, otp, 'user')
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

def forgot_password(request):
    return render(request, 'user/forgot_password.html')

def reset_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = request.session.get('reset_email')
            new_password = data.get('password')
            
            if not email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })

            # Check if OTP was verified
            if not ResetPasswordOTP.objects.filter(
                email=email,
                is_verified=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })

            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            
            # Clear session
            del request.session['reset_email']
            
            return JsonResponse({
                'status': 'success',
                'message': 'Password updated successfully'
            })
            
        except User.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return render(request, 'user/reset_password.html')

@csrf_exempt
def check_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            # Check if user exists
            exists = User.objects.filter(email=email).exists()
            
            return JsonResponse({
                'exists': exists
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            })
    
    return JsonResponse({'error': 'Invalid request method'})

@csrf_exempt
def send_reset_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            # Check if user exists
            if not User.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'No account found with this email'
                })

            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])

            # Delete any existing unverified OTPs
            ResetPasswordOTP.objects.filter(
                email=email,
                is_verified=False
            ).delete()

            # Save new OTP
            ResetPasswordOTP.objects.create(
                email=email,
                otp=otp,
                is_verified=False
            )

            # Send OTP email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return JsonResponse({
                'status': 'success',
                'message': 'OTP sent successfully'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

@csrf_exempt
def verify_reset_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')

            try:
                reset_otp = ResetPasswordOTP.objects.filter(
                    email=email,
                    is_verified=False
                ).latest('created_at')
            except ResetPasswordOTP.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'No OTP found. Please request a new one.'
                })

            if timezone.now() - reset_otp.created_at > timedelta(minutes=10):
                return JsonResponse({
                    'status': 'error',
                    'message': 'OTP has expired. Please request a new one.'
                })

            if reset_otp.otp == otp:
                reset_otp.is_verified = True
                reset_otp.save()
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

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Update basic info
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone:
            user.phone_number = phone

        # Update password if provided
        if current_password and new_password and confirm_password:
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect')
                return render(request, 'home/profile/edit-profile.html')
            if new_password != confirm_password:
                messages.error(request, 'New passwords do not match')
                return render(request, 'home/profile/edit-profile.html')
            user.set_password(new_password)

        user.save()
        messages.success(request, 'Profile updated successfully')
        return render(request, 'home/profile/edit-profile.html')

    return render(request, 'home/profile/edit-profile.html')

@login_required
def my_orders(request):
    return render(request, 'home/profile/my-orders.html')

@login_required
def favorites(request):
    # Add your favorites logic here
    return render(request, 'home/profile/favorites.html')

@login_required
def addresses(request):
    user = request.user
    addresses = []
    
    try:
        # Get non-empty addresses
        for i in range(1, 6):
            location = getattr(user, f'location{i}', '')
            if location:
                addresses.append({
                    'id': i,
                    'address': location
                })
    except AttributeError:
        # Handle case where fields don't exist yet
        pass
            
    return render(request, 'home/profile/addresses.html', {'addresses': addresses})

@login_required
def update_address(request):
    if request.method == 'POST':
        user = request.user
        address_id = request.POST.get('addressId')
        address = request.POST.get('address')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Combine address with coordinates
        full_address = f"{address} [{latitude}, {longitude}]"

        # Find first empty slot if adding new address
        if not address_id:
            for i in range(1, 6):
                if not getattr(user, f'location{i}'):
                    setattr(user, f'location{i}', full_address)
                    break
        else:
            # Update existing address
            setattr(user, f'location{address_id}', full_address)
        
        user.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def delete_address(request):
    if request.method == 'DELETE':
        user = request.user
        address_id = request.GET.get('id')
        if 1 <= int(address_id) <= 5:
            setattr(user, f'location{address_id}', '')
            user.save()
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_address(request):
    user = request.user
    address_id = request.GET.get('id')
    if 1 <= int(address_id) <= 5:
        address = getattr(user, f'location{address_id}')
        return JsonResponse({
            'id': address_id,
            'address': address
        })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def food_view(request):
    # Fetch all food items with their restaurant information
    food_items = FoodItem.objects.select_related('restaurant').all()
    
    context = {
        'food_items': food_items
    }
    return render(request, 'home/food.html', context)

@login_required
def quickbite_view(request):
    return render(request, 'home/quickbite.html')

@login_required
def dinespot_view(request):
    # Fetch all dining tables with their restaurant information
    dining_tables = DiningTable.objects.select_related('restaurant').all()
    
    context = {
        'dining_tables': dining_tables
    }
    return render(request, 'home/dinespot.html', context)

@login_required
def buzzfest_view(request):
    return render(request, 'home/buzzfest.html')

@login_required
def packages_view(request):
    return render(request, 'home/packages.html')

@login_required
def cart_view(request):
    return render(request, 'home/cart/cart.html')

@login_required
def update_location(request):
    if request.method == 'POST':
        location = request.POST.get('location')
        if location:
            user = request.user
            
            # Check if location already exists
            existing_locations = [
                user.location1, user.location2, user.location3,
                user.location4, user.location5
            ]
            existing_locations = [loc for loc in existing_locations if loc]  # Remove None values
            
            if location not in existing_locations:
                # Shift locations down
                if len(existing_locations) >= 5:
                    user.location5 = user.location4
                    user.location4 = user.location3
                    user.location3 = user.location2
                    user.location2 = user.location1
                    user.location1 = location
                else:
                    # Find first empty slot
                    for i in range(1, 6):
                        field_name = f'location{i}'
                        if not getattr(user, field_name):
                            setattr(user, field_name, location)
                            break
            
            # Update current location
            user.current_location = location
            user.save()
            
            # Update session
            request.session['user_location'] = location
            return JsonResponse({
                'status': 'success',
                'message': 'Location updated successfully'
            })
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })

@login_required
def payments_view(request):
    return render(request, 'home/payments/payments.html')

def partner(request):
    """
    Display partner landing page
    URL: /partner/
    Template: login/partner.html
    """
    return render(request, 'login/partner.html')

# Check for any notification-related views or context data 