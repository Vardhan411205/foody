from django.contrib.auth.models import User

class UserData:
    @staticmethod
    def get_user_display_name(user):
        """Get the user's display name from auth_user table"""
        try:
            # First check if user exists and is authenticated
            if not user or not user.is_authenticated:
                return "Guest User"
            
            # Get user from database to ensure fresh data
            user = User.objects.get(id=user.id)
            
            # Try to get full name
            full_name = f"{user.first_name} {user.last_name}".strip()
            if full_name:
                return full_name
            
            # If no full name, return email
            return user.email
        except User.DoesNotExist:
            return "Guest User"

    @staticmethod
    def get_user_data(user):
        """Get all relevant user data from auth_user table"""
        try:
            # First check if user exists and is authenticated
            if not user or not user.is_authenticated:
                return {
                    'name': "Guest User",
                    'email': None,
                    'is_authenticated': False
                }

            # Get fresh user data from database
            user = User.objects.get(id=user.id)
            
            return {
                'name': UserData.get_user_display_name(user),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_authenticated': True,
                'date_joined': user.date_joined,
                'username': user.username
            }
        except User.DoesNotExist:
            return {
                'name': "Guest User",
                'email': None,
                'is_authenticated': False
            } 