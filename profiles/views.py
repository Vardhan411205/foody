from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import UserProfile
import json

@login_required
def edit_profile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            profile = UserProfile.objects.get_or_create(user=user)[0]

            # Update user info
            user.first_name = data.get('name', '').split()[0]
            user.last_name = ' '.join(data.get('name', '').split()[1:])
            user.email = data.get('email', user.email)
            user.save()

            # Update profile info
            profile.phone = data.get('phone', profile.phone)
            if 'profile_photo' in request.FILES:
                profile.profile_photo = request.FILES['profile_photo']
            profile.save()

            return JsonResponse({
                'status': 'success',
                'data': {
                    'name': f"{user.first_name} {user.last_name}",
                    'email': user.email,
                    'phone': profile.phone,
                    'profile_photo': profile.profile_photo.url if profile.profile_photo else None
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'home/profile/edit-profile.html') 