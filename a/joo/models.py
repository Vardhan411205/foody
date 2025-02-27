from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.contrib.auth.models import User, AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import UserManager

class DeliveryPartner(models.Model):
    VEHICLE_CHOICES = [
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('cycle', 'Cycle'),
        ('auto', 'Auto'),
    ]

    HOURS_CHOICES = [
        ('morning', '6 AM - 12 PM'),
        ('afternoon', '12 PM - 6 PM'),
        ('evening', '6 PM - 12 AM'),
        ('night', '12 AM - 6 AM'),
        ('flexible', 'Flexible'),
    ]

    AREA_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('central', 'Central'),
        ('all', 'All Areas'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_CHOICES, default='bike')
    vehicle_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    preferred_hours = models.CharField(max_length=100, choices=HOURS_CHOICES, default='flexible')
    preferred_area = models.CharField(max_length=100, choices=AREA_CHOICES, default='all')
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'joo_deliverypartner'

    def __str__(self):
        return self.full_name

class RestaurantPartner(models.Model):
    restaurant_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    cuisine_type = models.CharField(max_length=50)
    address = models.TextField()
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    restaurant_image = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'joo_restaurantpartner'

    def __str__(self):
        return self.restaurant_name

class VenuePartner(models.Model):
    venue_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    venue_type = models.CharField(max_length=50)
    seating_capacity = models.IntegerField()
    address = models.TextField()
    venue_image = models.URLField(blank=True)  # Optional field
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'joo_venuepartner'

    def __str__(self):
        return self.venue_name

class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    partner_type = models.CharField(max_length=20)  # 'restaurant', 'delivery', 'venue'
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'joo_otpverification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.partner_type} - {self.created_at}"

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    partner_type = models.CharField(max_length=20)  # 'delivery', 'restaurant', or 'venue'
    created_at = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.email} - {self.partner_type} - Reset OTP"
    
    class Meta:
        get_latest_by = 'created_at'
        indexes = [
            models.Index(fields=['email', 'partner_type', 'created_at']),
        ]

class FoodItem(models.Model):
    restaurant = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.restaurant.restaurant_name}"

class DiningTable(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
    ]
    
    CATEGORY_CHOICES = [
        ('luxury', 'Luxury'),
        ('premium', 'Premium'),
        ('casual', 'Casual'),
        ('budget', 'Budget'),
    ]
    
    restaurant = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    table_number = models.CharField(max_length=20)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='casual')
    seating_capacity = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(20)],
        default=4  # Default capacity of 4 persons
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=500.00  # Default price of ₹500 per hour
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=5.0  # Default rating of 5.0
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image_url = models.URLField(default='https://via.placeholder.com/300')  # New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.table_number} - {self.restaurant.restaurant_name}"

    class Meta:
        ordering = ['table_number']

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    restaurant = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    table = models.ForeignKey(DiningTable, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    guest_count = models.IntegerField()
    booking_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for {self.customer_name} at {self.restaurant.restaurant_name}"

class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    venue = models.ForeignKey(VenuePartner, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    event_type = models.CharField(max_length=50)  # wedding, birthday, corporate, etc.
    event_date = models.DateTimeField()
    guest_count = models.IntegerField()
    package = models.ForeignKey('EventPackage', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_type} at {self.venue.venue_name} on {self.event_date}"

class EventPackage(models.Model):
    venue = models.ForeignKey(VenuePartner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.IntegerField()
    duration_hours = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.venue.venue_name}"

class ResetPasswordOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_resetpassword'
        get_latest_by = 'created_at'

    def __str__(self):
        return f"{self.email} - {self.created_at}"

class AccountOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20)  # signup, reset
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_otp'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.created_at}"

class PartnerOTPVerification(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=254)
    otp = models.CharField(max_length=6)
    partner_type = models.CharField(max_length=20)  # 'restaurant', 'delivery', 'venue'
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'partner_otp_verification'

class User(AbstractUser):
    current_location = models.CharField(max_length=255, blank=True, null=True)
    location1 = models.CharField(max_length=255, blank=True, null=True)
    location2 = models.CharField(max_length=255, blank=True, null=True)
    location3 = models.CharField(max_length=255, blank=True, null=True)
    location4 = models.CharField(max_length=255, blank=True, null=True)
    location5 = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'joo_user'  # Change from auth_user to joo_user
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email or self.username
