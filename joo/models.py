# Remove these models:
# - DeliveryPartner
# - RestaurantPartner
# - VenuePartner
# - FoodItem
# - DiningTable
# - Booking
# - Event
# - EventPackage

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    """Custom user model with additional location fields"""
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    current_location = models.CharField(max_length=255, default='', blank=True)
    location1 = models.CharField(max_length=255, default='', blank=True)
    location2 = models.CharField(max_length=255, default='', blank=True)
    location3 = models.CharField(max_length=255, default='', blank=True)
    location4 = models.CharField(max_length=255, default='', blank=True)
    location5 = models.CharField(max_length=255, default='', blank=True)

    class Meta:
        db_table = 'joo_user'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email or self.username


class AccountOTP(models.Model):
    """Model for handling signup and general OTP verification"""
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20)  # signup, reset
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'accounts_otp'
        ordering = ['-created_at']
        verbose_name = 'Account OTP'
        verbose_name_plural = 'Account OTPs'

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.created_at}"

    def is_expired(self):
        """Check if OTP is expired (valid for 10 minutes)"""
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiry_time


class ResetPasswordOTP(models.Model):
    """Model for handling password reset OTP verification"""
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_resetpassword'
        get_latest_by = 'created_at'
        verbose_name = 'Reset Password OTP'
        verbose_name_plural = 'Reset Password OTPs'

    def __str__(self):
        return f"{self.email} - {self.created_at}"

    def is_expired(self):
        """Check if reset OTP is expired (valid for 10 minutes)"""
        expiry_time = self.created_at + timezone.timedelta(minutes=10)
        return timezone.now() > expiry_time


class Address(models.Model):
    ADDRESS_TYPES = (
        ('home', 'Home'),
        ('work', 'Work'),
        ('other', 'Other')
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_addresses'
        ordering = ['-is_default', '-updated_at']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.user.email} - {self.address_type} - {self.address[:50]}"


class Order(models.Model):
    ORDER_TYPES = (
        ('food', 'Food Order'),
        ('dining', 'Dine Spot'),
        ('venue', 'Buzz Fest Venue')
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    )
    
    order_id = models.CharField(max_length=50, unique=True)
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    customer_email = models.CharField(max_length=255)
    restaurant_id = models.IntegerField()
    restaurant_email = models.CharField(max_length=255, blank=True)
    restaurant_name = models.CharField(max_length=255)
    booking_date = models.DateTimeField()
    items = models.TextField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'joo_order'
        ordering = ['-booking_date']

    def __str__(self):
        return f"Order {self.order_id} - {self.restaurant_name}"

    def save(self, *args, **kwargs):
        if not self.booking_date.tzinfo:
            self.booking_date = timezone.make_aware(self.booking_date)
        super().save(*args, **kwargs)


class TableBooking(models.Model):
    id = models.AutoField(primary_key=True)
    booking_id = models.CharField(max_length=255, unique=True)
    customer_email = models.CharField(max_length=255, null=False)
    restaurant_id = models.IntegerField(null=False)
    restaurant_name = models.CharField(max_length=255, null=False)
    table_number = models.IntegerField(null=False)
    seating_capacity = models.IntegerField(null=False)
    booking_date = models.DateField(null=False)
    time_slot = models.CharField(max_length=20, null=False)  # morning, afternoon, evening
    status = models.CharField(max_length=20, null=False, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'joo_tablebooking'
        ordering = ['-booking_date', '-created_at']

    def __str__(self):
        return f"Booking {self.booking_id} - {self.restaurant_name}"
