from django.test import TestCase, Client
from django.urls import reverse
from .models import User, AccountOTP, ResetPasswordOTP
import json

# Create your tests here.

class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.test_user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )

    def test_signup(self):
        """Test user signup functionality"""
        url = reverse('joo:signup')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123'
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_login(self):
        """Test user login functionality"""
        url = reverse('joo:login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')

    def test_send_otp(self):
        """Test OTP sending functionality"""
        url = reverse('joo:send_otp')
        data = {
            'email': 'test@example.com'
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
        self.assertTrue(AccountOTP.objects.filter(email='test@example.com').exists())

    def test_verify_otp(self):
        """Test OTP verification functionality"""
        # Create an OTP first
        otp = AccountOTP.objects.create(
            email='test@example.com',
            otp='1234',
            purpose='signup'
        )
        
        url = reverse('joo:verify_otp')
        data = {
            'email': 'test@example.com',
            'otp': '1234'
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
        
        # Check if OTP was marked as verified
        otp.refresh_from_db()
        self.assertTrue(otp.is_verified)

    def test_password_reset_flow(self):
        """Test complete password reset flow"""
        # Test sending reset OTP
        url = reverse('joo:send-reset-otp')
        data = {
            'email': 'test@example.com'
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
        
        # Test verifying reset OTP
        otp = ResetPasswordOTP.objects.get(email='test@example.com')
        url = reverse('joo:verify-reset-otp')
        data = {
            'email': 'test@example.com',
            'otp': otp.otp
        }
        response = self.client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['status'], 'success')
