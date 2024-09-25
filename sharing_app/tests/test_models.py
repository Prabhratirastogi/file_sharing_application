from django.test import TestCase
from sharing_app.models import User, File, VerificationToken
from django.utils import timezone
from datetime import timedelta

class UserModelTest(TestCase):
    def setUp(self):
        # Create a user instance for testing
        self.user = User.objects.create_user(email='test@example.com', password='password123', username='testuser', user_type='client_user')

    def test_user_creation(self):
        # Test if user was created correctly
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.user_type, 'client_user')
        self.assertFalse(self.user.is_verified)

    def test_unique_email(self):
        # Test that an error is raised when trying to create a user with a duplicate email
        with self.assertRaises(Exception):
            User.objects.create_user(email='test@example.com', password='password123', username='anotheruser', user_type='ops_user')

    def test_user_type_choices(self):
        # Test that the user_type field only accepts valid choices
        valid_user_types = ['ops_user', 'client_user']
        for user_type in valid_user_types:
            user = User(email=f'test{user_type}@example.com', password='password123', username='testuser', user_type=user_type)
            user.save()
            self.assertEqual(user.user_type, user_type)

class FileModelTest(TestCase):
    def setUp(self):
        # Create a user instance
        self.user = User.objects.create_user(email='test@example.com', password='password123', username='testuser', user_type='ops_user')
        # Create a file instance for testing
        self.file = File.objects.create(file='uploads/test_file.pptx', uploaded_by=self.user)

    def test_file_creation(self):
        # Test if the file was created correctly
        self.assertEqual(self.file.uploaded_by.email, 'test@example.com')
        self.assertEqual(self.file.file.name, 'uploads/test_file.pptx')

    def test_file_upload_date(self):
        # Test if the upload_date is set to the current time on creation
        self.assertIsNotNone(self.file.upload_date)

class VerificationTokenModelTest(TestCase):
    def setUp(self):
        # Create a user instance
        self.user = User.objects.create_user(email='test@example.com', password='password123', username='testuser', user_type='client_user')
        # Create a verification token instance for the user
        self.token = VerificationToken.objects.create(user=self.user)

    def test_token_creation(self):
        # Test if the token was created correctly
        self.assertEqual(self.token.user, self.user)
        self.assertIsNotNone(self.token.token)

    def test_token_expiry(self):
        # Test if the token's expiry date is set correctly
        self.assertEqual(self.token.expiry_date, self.token.created_at + timedelta(hours=24))

    def test_is_expired(self):
        # Test if the is_expired method works correctly
        self.token.expiry_date = timezone.now() - timedelta(days=1)  # Set to a past date
        self.assertTrue(self.token.is_expired())
        
        self.token.expiry_date = timezone.now() + timedelta(days=1)  # Set to a future date
        self.assertFalse(self.token.is_expired())
