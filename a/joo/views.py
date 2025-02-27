from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
import json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
import hashlib
from django.core.mail import send_mail
from django.conf import settings
from functools import wraps
from django.db import connection

from .models import (
    DeliveryPartner, 
    RestaurantPartner, 
    VenuePartner, 
    OTPVerification,
    PasswordResetOTP, 
    FoodItem, 
    DiningTable, 
    Booking, 
    Event, 
    EventPackage
)

from .forgot_password import ForgotPasswordHandler
from .food_items import FoodItemManager
from .decorators import restaurant_required
from .accounts_otp import send_otp, verify_otp, is_email_verified

# Create your views here.

# User view
def user(request):
    """
    View for user login page
    URL: /user/
    Template: login/user.html
    """
    try:
        return render(request, 'login/user.html')
    except Exception as e:
        messages.error(request, f"Error loading user page: {str(e)}")
        return redirect('joo:partner')

# Partner main page
def partner(request):
    """Display partner landing page"""
    return render(request, 'login/partner.html')

# Login views
@csrf_exempt
def delivery_login(request):
    """Handle delivery partner login"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            print(f"Login attempt - Email: {email}")  # Debug log
            
            delivery = DeliveryPartner.objects.filter(email=email).first()
            
            if delivery:
                print(f"Found delivery partner: ID={delivery.id}, Email={delivery.email}")  # Debug log
                
                stored_password = delivery.password
                input_password = password
                hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
                
                if stored_password == hashed_input:
                    # Store session data
                    request.session['delivery_id'] = delivery.id
                    request.session['delivery_name'] = delivery.full_name
                    request.session['delivery_email'] = delivery.email
                    
                    print("Login successful - Session data stored")  # Debug log
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Login successful',
                        'redirect_url': reverse('joo:delivery_dashboard')
                    })
                else:
                    print("Password mismatch")  # Debug log
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid password'
                    })
            else:
                print(f"No delivery partner found with email: {email}")  # Debug log
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email not found'
                })
                
        except Exception as e:
            print(f"Login error: {str(e)}")  # Debug log
            return JsonResponse({
                'status': 'error',
                'message': 'Login failed. Please try again.'
            })
    
    return render(request, 'login/partner/login/delivery_login.html')

@csrf_exempt
def restaurant_login(request):
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Hash the provided password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Try to find the restaurant partner
            restaurant = RestaurantPartner.objects.get(
                email=email,
                password=hashed_password,
                is_active=True
            )
            
            # Store restaurant info in session
            request.session['restaurant_id'] = restaurant.id
            request.session['restaurant_name'] = restaurant.restaurant_name
            request.session['restaurant_email'] = restaurant.email
            
            return JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'redirect_url': reverse('joo:restaurant_dashboard')
            })
            
        except RestaurantPartner.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid email or password'
            })
        except Exception as e:
            print(f"Login error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': f'Login failed: {str(e)}'
            })
    
    return render(request, 'login/partner/login/restaurant_login.html')

@csrf_exempt
def venue_login(request):
    """Handle venue partner login"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            print(f"Login attempt - Email: {email}")
            
            venue = VenuePartner.objects.filter(email=email).first()
            
            if venue:
                print(f"Found venue: ID={venue.id}, Email={venue.email}")
                
                stored_password = venue.password
                input_password = password
                hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
                
                if stored_password == hashed_input:
                    # Store session data
                    request.session['venue_id'] = venue.id
                    request.session['venue_name'] = venue.venue_name
                    
                    # Handle venue image - check if it's an ImageField
                    if hasattr(venue, 'venue_image') and venue.venue_image:
                        if hasattr(venue.venue_image, 'url'):
                            request.session['venue_image'] = venue.venue_image.url
                        else:
                            request.session['venue_image'] = str(venue.venue_image)
                    
                    print("Login successful - Session data stored")
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Login successful',
                        'redirect_url': reverse('joo:venue_dashboard')
                    })
                else:
                    print("Password mismatch")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid password'
                    })
            else:
                print(f"No venue found with email: {email}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email not found'
                })
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Login failed. Please try again.'
            })
    
    return render(request, 'login/partner/login/venue_login.html')

# Registration views
def delivery(request):
    """Display delivery partner registration"""
    return render(request, 'login/partner/register/delivery.html')

def restaurant(request):
    """Display restaurant partner registration"""
    return render(request, 'login/partner/register/restaurant.html')

def venue(request):
    """Display venue partner registration"""
    return render(request, 'login/partner/register/venue.html')

@csrf_exempt
def send_otp_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            purpose = data.get('purpose', 'signup')
            
            if not email:
                return JsonResponse({'status': 'error', 'message': 'Email is required'})
            
            # Use the new functions directly
            result = send_otp(email, purpose)
            return JsonResponse(result)
            
        except Exception as e:
            print(f"Error sending OTP: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

@csrf_exempt
def verify_otp_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')
            purpose = data.get('purpose', 'signup')
            
            # Use the new functions directly
            result = verify_otp(email, otp, purpose)
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

@csrf_exempt
def register_delivery_partner(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            print(f"Checking OTP verification for email: {email}")  # Debug log
            
            # Check if email exists
            if DeliveryPartner.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already registered'
                })

            # Check if email is verified
            if not is_email_verified(email, 'delivery'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email not verified'
                })

            # Verify OTP first
            otp_verification = OTPVerification.objects.filter(
                email=email,
                partner_type='delivery',
                is_verified=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).first()

            if not otp_verification:
                print(f"No valid OTP verification found for email: {email}")  # Debug log
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })

            print(f"OTP verification found: {otp_verification}")  # Debug log

            # Hash password
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()

            # Create delivery partner
            partner = DeliveryPartner.objects.create(
                full_name=data['full_name'],
                email=data['email'],
                phone=data['phone'],
                address=data['address'],
                vehicle_type=data['vehicle_type'],
                vehicle_number=data['vehicle_number'],
                license_number=data['license_number'],
                preferred_hours=data['preferred_hours'],
                preferred_area=data['preferred_area'],
                password=hashed_password
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Registration successful!'
            })

        except Exception as e:
            print(f"Registration error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def register_restaurant_partner(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if email exists
            if RestaurantPartner.objects.filter(email=data['email']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already registered'
                })

            # Verify OTP first
            otp_verified = OTPVerification.objects.filter(
                email=data['email'],
                partner_type='restaurant',
                is_verified=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).exists()

            if not otp_verified:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })

            # Hash password
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()

            # Create restaurant partner
            partner = RestaurantPartner.objects.create(
                restaurant_name=data['restaurant_name'],
                owner_name=data['owner_name'],
                email=data['email'],
                phone=data['phone'],
                cuisine_type=data['cuisine_type'],
                address=data['address'],
                password=hashed_password
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Registration successful!'
            })

        except Exception as e:
            print(f"Registration error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def register_venue_partner(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if email exists
            if VenuePartner.objects.filter(email=data['email']).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already registered'
                })

            # Verify OTP first
            otp_verified = OTPVerification.objects.filter(
                email=data['email'],
                partner_type='venue',
                is_verified=True,
                created_at__gte=timezone.now() - timedelta(minutes=30)
            ).exists()

            if not otp_verified:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })

            # Hash password
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()

            # Create venue partner
            partner = VenuePartner.objects.create(
                venue_name=data['venue_name'],
                owner_name=data['owner_name'],
                email=data['email'],
                phone=data['phone'],
                venue_type=data['venue_type'],
                seating_capacity=data['seating_capacity'],
                address=data['address'],
                venue_image=data.get('venue_image', ''),  # Optional field
                password=hashed_password
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Registration successful!'
            })

        except Exception as e:
            print(f"Registration error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def forgot_password(request):
    """Handle partner forgot password"""
    return render(request, 'partner/forgot_password.html')

@csrf_exempt
def verify_reset_otp(request):
    """Handle partner OTP verification"""
    return render(request, 'partner/verify_reset_otp.html')

@csrf_exempt
def reset_password(request):
    """Handle partner password reset"""
    return render(request, 'partner/reset_password.html')

def terms_conditions(request):
    """
    View for terms and conditions page
    URL: /terms-conditions/
    Template: login/terms_conditions.html
    """
    try:
        return render(request, 'login/terms_conditions.html')
    except Exception as e:
        print(f"Error in terms_conditions view: {str(e)}")
        messages.error(request, "Error loading terms and conditions page")
        return redirect('joo:partner')

def restaurant_dashboard(request):
    """Display restaurant partner dashboard"""
    # Check if restaurant is logged in
    if 'restaurant_id' not in request.session:
        messages.error(request, "Please login first")
        return redirect('joo:restaurant_login')
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        return render(request, 'partner/restaurant/restaurant_dashboard.html', {
            'restaurant': restaurant
        })
    except RestaurantPartner.DoesNotExist:
        messages.error(request, "Restaurant not found")
        return redirect('joo:restaurant_login')

def venue_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'venue_id' not in request.session:
            return redirect('joo:venue_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@venue_login_required
def venue_dashboard(request):
    """Display venue partner dashboard"""
    if 'venue_id' not in request.session:
        messages.error(request, "Please login first")
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        # Get some basic stats
        total_events = Event.objects.filter(venue=venue).count()
        upcoming_events = Event.objects.filter(
            venue=venue,
            event_date__gte=timezone.now()
        ).count()
        active_packages = EventPackage.objects.filter(
            venue=venue,
            is_active=True
        ).count()
        
        context = {
            'venue': venue,
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'active_packages': active_packages
        }
        
        return render(request, 'partner/venue/venue_dashboard.html', context)
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')
    except Exception as e:
        print(f"Error in venue_dashboard: {str(e)}")
        return render(request, 'partner/venue/venue_dashboard.html', {
            'venue': None,
            'error_message': 'An error occurred loading the dashboard'
        })

def delivery_dashboard(request):
    """Display delivery partner dashboard"""
    if 'delivery_id' not in request.session:
        return redirect('joo:delivery_login')
    
    try:
        delivery = DeliveryPartner.objects.get(id=request.session['delivery_id'])
        
        # Get today's date
        today = timezone.now().date()
        
        context = {
            'delivery': delivery,
            'todays_deliveries': 0,  # Add your delivery count logic
            'todays_earnings': 0,    # Add your earnings logic
            'rating': 0.0,           # Add your rating logic
            'active_hours': 0        # Add your hours logic
        }
        
        return render(request, 'partner/delivery/delivery_dashboard.html', context)
        
    except DeliveryPartner.DoesNotExist:
        messages.error(request, "Delivery partner not found")
        return redirect('joo:delivery_login')

def logout(request):
    # Clear all session data
    request.session.flush()
    return redirect('joo:partner')

def restaurant_logout(request):
    """Handle restaurant partner logout"""
    # Clear restaurant session data
    request.session.pop('restaurant_id', None)
    request.session.pop('restaurant_name', None)
    request.session.pop('restaurant_email', None)
    return redirect('joo:restaurant_login')

@csrf_exempt
def update_restaurant_profile(request):
    """Handle restaurant profile editing"""
    if 'restaurant_id' not in request.session:
        return redirect('joo:restaurant_login')
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        
        if request.method == 'POST':
            try:
                # Update basic info
                restaurant.restaurant_name = request.POST.get('restaurant_name', restaurant.restaurant_name)
                restaurant.owner_name = request.POST.get('owner_name', restaurant.owner_name)
                restaurant.email = request.POST.get('email', restaurant.email)
                restaurant.phone = request.POST.get('phone', restaurant.phone)
                restaurant.address = request.POST.get('address', restaurant.address)
                restaurant.restaurant_image = request.POST.get('restaurant_image', restaurant.restaurant_image)
                
                restaurant.save()
                
                # Update session data
                request.session['restaurant_name'] = restaurant.restaurant_name
                request.session['restaurant_image'] = restaurant.restaurant_image
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Profile updated successfully'
                    })
                else:
                    messages.success(request, 'Profile updated successfully')
                    return redirect('joo:update_restaurant_profile')
                
            except Exception as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': str(e)
                    })
                else:
                    messages.error(request, f'Error updating profile: {str(e)}')
        
        return render(request, 'partner/restaurant/edit_profile.html', {
            'restaurant': restaurant
        })
        
    except RestaurantPartner.DoesNotExist:
        messages.error(request, "Restaurant not found")
        return redirect('joo:restaurant_login')

@csrf_exempt
def restaurant_food_items(request):
    """Handle restaurant food items"""
    if 'restaurant_id' not in request.session:
        return redirect('joo:restaurant_login')
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        
        if request.method == 'POST':
            try:
                # Parse JSON data if it's an AJAX request
                if request.headers.get('Content-Type') == 'application/json':
                    data = json.loads(request.body)
                    name = data.get('name')
                    price = data.get('price')
                    category = data.get('category')
                    image_url = data.get('image_url')
                    rating = data.get('rating', 0)
                    is_available = data.get('is_available', True)  # Default to True if not provided
                else:
                    # Get data from POST request
                    name = request.POST.get('name')
                    price = request.POST.get('price')
                    category = request.POST.get('category')
                    image_url = request.POST.get('image_url')
                    rating = request.POST.get('rating', 0)
                    is_available = request.POST.get('is_available', 'true') == 'true'

                # Create new food item
                food_item = FoodItem.objects.create(
                    restaurant=restaurant,
                    name=name,
                    price=price,
                    category=category,
                    image_url=image_url,
                    rating=rating,
                    is_available=is_available
                )

                return JsonResponse({
                    'status': 'success',
                    'message': 'Food item added successfully',
                    'item': {
                        'id': food_item.id,
                        'name': food_item.name,
                        'price': float(food_item.price),
                        'category': food_item.category,
                        'image_url': food_item.image_url,
                        'rating': float(food_item.rating),
                        'is_available': food_item.is_available
                    }
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        
        # Get all food items for this restaurant
        food_items = FoodItem.objects.filter(restaurant=restaurant).order_by('category', 'name')
        
        return render(request, 'partner/restaurant/food_items.html', {
            'restaurant': restaurant,
            'food_items': food_items
        })
        
    except RestaurantPartner.DoesNotExist:
        messages.error(request, "Restaurant not found")
        return redirect('joo:restaurant_login')

@csrf_exempt
def restaurant_dining_tables(request):
    """Handle restaurant dining tables"""
    if 'restaurant_id' not in request.session:
        return redirect('joo:restaurant_login')
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        
        if request.method == 'POST':
            try:
                # Parse JSON data if it's an AJAX request
                if request.headers.get('Content-Type') == 'application/json':
                    data = json.loads(request.body)
                    action = data.get('action')
                    
                    if action == 'add':
                        table = DiningTable.objects.create(
                            restaurant=restaurant,
                            table_number=data.get('table_number'),
                            category=data.get('category'),
                            seating_capacity=data.get('seating_capacity'),
                            price=data.get('price'),
                            rating=data.get('rating'),
                            status=data.get('status'),
                            image_url=data.get('image_url')
                        )
                        
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Table added successfully',
                            'table': {
                                'id': table.id,
                                'table_number': table.table_number,
                                'category': table.category,
                                'seating_capacity': table.seating_capacity,
                                'price': float(table.price),
                                'rating': float(table.rating),
                                'status': table.status,
                                'image_url': table.image_url
                            }
                        })
                    
                    # Handle other actions (edit, delete) here...
                
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid action'
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        
        # Get all tables for this restaurant
        tables = DiningTable.objects.filter(restaurant=restaurant).order_by('table_number')
        
        return render(request, 'partner/restaurant/dining_tables.html', {
            'restaurant': restaurant,
            'tables': tables
        })
        
    except RestaurantPartner.DoesNotExist:
        messages.error(request, "Restaurant not found")
        return redirect('joo:restaurant_login')

@csrf_exempt
def restaurant_booking_history(request):
    """Handle restaurant booking history view"""
    if 'restaurant_id' not in request.session:
        return redirect('joo:restaurant_login')
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        
        # Get all bookings for this restaurant
        bookings = Booking.objects.filter(restaurant=restaurant).order_by('-created_at')
        
        # Convert bookings to list of dictionaries for JSON response
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'customer_name': booking.customer_name,
                'customer_phone': booking.customer_phone,
                'table_number': booking.table.table_number,
                'guest_count': booking.guest_count,
                'booking_date': booking.booking_date.strftime('%Y-%m-%d %H:%M'),
                'status': booking.status,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        if request.method == 'GET':
            return render(request, 'partner/restaurant/booking_history.html', {
                'restaurant': restaurant,
                'bookings': bookings,
                'status_choices': Booking.STATUS_CHOICES
            })
        
        # For AJAX requests, return JSON data
        return JsonResponse({
            'status': 'success',
            'bookings': bookings_data
        })
        
    except RestaurantPartner.DoesNotExist:
        messages.error(request, "Restaurant not found")
        return redirect('joo:restaurant_login')
    except Exception as e:
        print(f"Error loading booking history: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error loading booking history: {str(e)}'
        })

@csrf_exempt
def update_booking_status(request):
    """Handle updating booking status"""
    if 'restaurant_id' not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Please login first'
        })
    
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        })
    
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        new_status = data.get('status')
        
        if not booking_id or not new_status:
            return JsonResponse({
                'status': 'error',
                'message': 'Booking ID and new status are required'
            })
        
        # Get the booking and verify it belongs to this restaurant
        booking = Booking.objects.get(
            id=booking_id,
            restaurant_id=request.session['restaurant_id']
        )
        
        # Validate the new status
        if new_status not in dict(Booking.STATUS_CHOICES):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid status value'
            })
        
        # Update the status
        booking.status = new_status
        booking.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Booking status updated successfully',
            'new_status': new_status,
            'booking_id': booking_id
        })
        
    except Booking.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Booking not found or access denied'
        })
    except Exception as e:
        print(f"Error updating booking status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error updating status: {str(e)}'
        })

@csrf_exempt
def venue_edit_profile(request):
    """Handle venue partner profile editing"""
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        if request.method == 'POST':
            try:
                # Handle AJAX requests for profile updates
                if request.headers.get('Content-Type') == 'application/json':
                    data = json.loads(request.body)
                    
                    # Update venue fields
                    venue.venue_name = data.get('venue_name', venue.venue_name)
                    venue.owner_name = data.get('owner_name', venue.owner_name)
                    venue.email = data.get('email', venue.email)
                    venue.phone = data.get('phone', venue.phone)
                    venue.venue_type = data.get('venue_type', venue.venue_type)
                    venue.seating_capacity = data.get('seating_capacity', venue.seating_capacity)
                    venue.address = data.get('address', venue.address)
                    venue.venue_image = data.get('venue_image', venue.venue_image)
                    
                    venue.save()
                    
                    # Update session data
                    request.session['venue_name'] = venue.venue_name
                    request.session['venue_image'] = venue.venue_image
                    
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Profile updated successfully'
                    })
                
                # Handle form submissions
                venue.venue_name = request.POST.get('venue_name', venue.venue_name)
                venue.owner_name = request.POST.get('owner_name', venue.owner_name)
                venue.email = request.POST.get('email', venue.email)
                venue.phone = request.POST.get('phone', venue.phone)
                venue.venue_type = request.POST.get('venue_type', venue.venue_type)
                venue.seating_capacity = request.POST.get('seating_capacity', venue.seating_capacity)
                venue.address = request.POST.get('address', venue.address)
                venue.venue_image = request.POST.get('venue_image', venue.venue_image)
                
                venue.save()
                
                # Update session data
                request.session['venue_name'] = venue.venue_name
                request.session['venue_image'] = venue.venue_image
                
                messages.success(request, 'Profile updated successfully')
                
            except Exception as e:
                messages.error(request, f'Error updating profile: {str(e)}')
        
        # Render the edit profile template
        return render(request, 'partner/venue/edit_profile.html', {
            'venue': venue
        })
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')

@csrf_exempt
def venue_packages(request):
    """Handle venue packages view"""
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        # Get all packages for this venue
        packages = EventPackage.objects.filter(venue=venue).order_by('price')
        
        # Convert packages to list of dictionaries for JSON response
        packages_data = []
        for package in packages:
            packages_data.append({
                'id': package.id,
                'name': package.name,
                'description': package.description,
                'price': float(package.price),
                'max_guests': package.max_guests,
                'duration_hours': package.duration_hours,
                'is_active': package.is_active
            })
        
        if request.method == 'GET':
            return render(request, 'partner/venue/packages.html', {
                'venue': venue,
                'packages': packages
            })
        
        # For AJAX requests, return JSON data
        return JsonResponse({
            'status': 'success',
            'packages': packages_data
        })
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')
    except Exception as e:
        print(f"Error loading packages: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error loading packages: {str(e)}'
        })

@csrf_exempt
def venue_events(request):
    """Handle venue events view"""
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        # Get all events for this venue
        events = Event.objects.filter(venue=venue).order_by('-event_date')
        
        # Convert events to list of dictionaries for JSON response
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'customer_name': event.customer_name,
                'customer_phone': event.customer_phone,
                'event_type': event.event_type,
                'event_date': event.event_date.strftime('%Y-%m-%d %H:%M'),
                'guest_count': event.guest_count,
                'package': event.package.name if event.package else None,
                'status': event.status,
                'rating': float(event.rating) if event.rating else None,
                'created_at': event.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        if request.method == 'GET':
            return render(request, 'partner/venue/events.html', {
                'venue': venue,
                'events': events,
                'status_choices': Event.STATUS_CHOICES
            })
        
        # For AJAX requests, return JSON data
        return JsonResponse({
            'status': 'success',
            'events': events_data
        })
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')
    except Exception as e:
        print(f"Error loading events: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error loading events: {str(e)}'
        })

@csrf_exempt
def update_event_status(request):
    """Handle updating event status"""
    if 'venue_id' not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Please login first'
        })
    
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        })
    
    try:
        data = json.loads(request.body)
        event_id = data.get('event_id')
        new_status = data.get('status')
        
        if not event_id or not new_status:
            return JsonResponse({
                'status': 'error',
                'message': 'Event ID and new status are required'
            })
        
        # Get the event and verify it belongs to this venue
        event = Event.objects.get(
            id=event_id,
            venue_id=request.session['venue_id']
        )
        
        # Validate the new status
        if new_status not in dict(Event.STATUS_CHOICES):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid status value'
            })
        
        # Update the status
        event.status = new_status
        event.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Event status updated successfully',
            'new_status': new_status,
            'event_id': event_id
        })
        
    except Event.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Event not found or access denied'
        })
    except Exception as e:
        print(f"Error updating event status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error updating status: {str(e)}'
        })

@csrf_exempt
def venue_bookings(request):
    """Handle venue bookings view"""
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        # Get all current and upcoming bookings
        bookings = Event.objects.filter(
            venue=venue,
            event_date__gte=timezone.now()
        ).order_by('event_date')
        
        # Convert bookings to list of dictionaries for JSON response
        bookings_data = []
        for booking in bookings:
            bookings_data.append({
                'id': booking.id,
                'customer_name': booking.customer_name,
                'customer_phone': booking.customer_phone,
                'event_type': booking.event_type,
                'event_date': booking.event_date.strftime('%Y-%m-%d %H:%M'),
                'guest_count': booking.guest_count,
                'package': booking.package.name if booking.package else None,
                'status': booking.status,
                'created_at': booking.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        if request.method == 'GET':
            return render(request, 'partner/venue/bookings.html', {
                'venue': venue,
                'bookings': bookings,
                'status_choices': Event.STATUS_CHOICES
            })
        
        # For AJAX requests, return JSON data
        return JsonResponse({
            'status': 'success',
            'bookings': bookings_data
        })
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')
    except Exception as e:
        print(f"Error loading bookings: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error loading bookings: {str(e)}'
        })

@csrf_exempt
def venue_logout(request):
    """Handle venue partner logout"""
    # Clear all venue-related session data
    keys_to_remove = [
        'venue_id',
        'venue_name',
        'venue_email'
    ]
    
    for key in keys_to_remove:
        request.session.pop(key, None)
    
    # Flush the entire session
    request.session.flush()
    
    # Redirect to venue login page
    return redirect('joo:venue_login')

@csrf_exempt
def delivery_edit_profile(request):
    """Handle delivery partner profile editing"""
    if 'delivery_id' not in request.session:
        return redirect('joo:delivery_login')
    
    try:
        delivery = DeliveryPartner.objects.get(id=request.session['delivery_id'])
        
        if request.method == 'POST':
            try:
                # Update basic info
                delivery.full_name = request.POST.get('full_name', delivery.full_name)
                delivery.phone = request.POST.get('phone', delivery.phone)
                delivery.vehicle_type = request.POST.get('vehicle_type', delivery.vehicle_type)
                delivery.vehicle_number = request.POST.get('vehicle_number', delivery.vehicle_number)
                delivery.license_number = request.POST.get('license_number', delivery.license_number)
                
                # Handle password update
                new_password = request.POST.get('new_password')
                if new_password:
                    delivery.password = hashlib.sha256(new_password.encode()).hexdigest()
                
                delivery.save()
                
                # Update session data
                request.session['delivery_name'] = delivery.full_name
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profile updated successfully'
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        
        # For GET requests, render the template
        return render(request, 'partner/delivery/edit_profile.html', {
            'delivery': delivery
        })
        
    except DeliveryPartner.DoesNotExist:
        messages.error(request, "Delivery partner not found")
        return redirect('joo:delivery_login')

@csrf_exempt
def delivery_logout(request):
    """Handle delivery partner logout"""
    # Clear all delivery-related session data
    keys_to_remove = [
        'delivery_id',
        'delivery_name',
        'delivery_email'
    ]
    
    for key in keys_to_remove:
        request.session.pop(key, None)
    
    # Flush the entire session
    request.session.flush()
    
    # Redirect to delivery login page
    return redirect('joo:delivery_login')
        