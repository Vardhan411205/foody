from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from profiles.models import UserProfile
from django.contrib.auth.decorators import login_required

def index(request):
    context = {}
    if request.user.is_authenticated:
        profile = UserProfile.objects.get_or_create(user=request.user)[0]
        context = {
            'name': request.user.get_full_name() or request.user.email,
            'email': request.user.email,
            'profile_photo': profile.profile_photo.url if profile.profile_photo else None,
            'phone': profile.phone
        }
    return render(request, 'home/index.html', context)

def food(request):
    return render(request, 'home/food.html')

def dinespot(request):
    return render(request, 'home/dinespot.html')

def quickbite(request):
    return render(request, 'home/quickbite.html')

def buzzfest(request):
    return render(request, 'home/buzzfest.html')

def packages(request):
    return render(request, 'home/packages.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        try:
            user = request.user
            profile = UserProfile.objects.get_or_create(user=user)[0]

            # Update user info
            name = request.POST.get('name', '').strip()
            if ' ' in name:
                first_name, last_name = name.split(' ', 1)
            else:
                first_name, last_name = name, ''
            
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Update profile info
            profile.phone = request.POST.get('phone', profile.phone)
            if 'profile_photo' in request.FILES:
                profile.profile_photo = request.FILES['profile_photo']
            profile.save()

            return JsonResponse({
                'status': 'success',
                'email': user.email,
                'name': user.get_full_name() or user.email,
                'phone': profile.phone,
                'profile_photo': profile.profile_photo.url if profile.profile_photo else None
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    # For GET requests, get the current user data
    user = request.user
    profile = UserProfile.objects.get_or_create(user=user)[0]
    context = {
        'name': user.get_full_name() or user.email,
        'email': user.email,
        'phone': profile.phone,
        'profile_photo': profile.profile_photo.url if profile.profile_photo else None
    }
    return render(request, 'home/profile/user_edit_profile.html', context)

@login_required
def my_orders(request):
    return render(request, 'home/profile/my-orders.html')

@login_required
def favorites(request):
    return render(request, 'home/profile/favorites.html')

@login_required
def addresses(request):
    return render(request, 'home/profile/addresses.html')

@login_required
def cart(request):
    return render(request, 'home/cart/cart.html')

@login_required
def payments(request):
    return render(request, 'home/payments/payments.html')

@ensure_csrf_cookie
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                
                # Get or create user profile
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                return JsonResponse({
                    'status': 'success',
                    'email': user.email,
                    'name': f"{user.first_name} {user.last_name}",
                    'phone': profile.phone,
                    'profile_photo': profile.profile_photo.url if profile.profile_photo else None
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid credentials'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
            
    return render(request, 'user/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('user:login') 