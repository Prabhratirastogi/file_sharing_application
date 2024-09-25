from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from sharing_app.models import User, File
from sharing_app.serializers import (
    UserSignupSerializer, 
    FileUploadSerializer, 
    UserLoginSerializer, 
    FileListSerializer
)
import os
import tempfile

class UserSignupSerializerTests(APITestCase):
    
    def test_valid_signup_data(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'securepassword',
            'user_type': 'client_user'
        }
        serializer = UserSignupSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('securepassword'))
        self.assertEqual(user.user_type, 'client_user')

    def test_email_already_exists(self):
        User.objects.create_user(
            username='existinguser',
            email='existinguser@example.com',
            password='securepassword',
            user_type='ops_user'
        )
        data = {
            'username': 'testuser',
            'email': 'existinguser@example.com',
            'password': 'securepassword',
            'user_type': 'client_user'
        }
        serializer = UserSignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class FileUploadSerializerTests(APITestCase):
    def test_valid_file_upload(self):
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='securepassword',
            user_type='ops_user'
        )
        
        # Force authentication for the user
        self.client.force_authenticate(user=user)

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            temp_file.write(b'This is a test file.')
            temp_file_path = temp_file.name  # Store the file path

        try:
            with open(temp_file_path, 'rb') as f:
                response = self.client.post(
                    reverse('file-upload'),  # Adjust the reverse URL according to your URL configuration
                    {'file': f},  # Ensure the file is uploaded in the correct format
                    format='multipart'  # Use multipart to simulate file upload
                )
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Check for successful creation

                # Verify that the file is created correctly
                self.assertTrue(File.objects.filter(uploaded_by=user).exists())
        finally:
            # Clean up the temporary file
            os.remove(temp_file_path)  # Ensure this runs after file usage

    

    
    def test_invalid_file_type(self):
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
            temp_file.write(b'This is a test file.')
            temp_file_path = temp_file.name

        with open(temp_file_path, 'rb') as f:
            data = {'file': f}
            serializer = FileUploadSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn('file', serializer.errors)

        # Clean up the temporary file
        os.remove(temp_file_path)

class UserLoginSerializerTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='securepassword',
            user_type='client_user',
            is_verified=True
        )

    def test_valid_login(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'securepassword'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_invalid_login(self):
        data = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_email_not_verified(self):
        self.user.is_verified = False
        self.user.save()
        data = {
            'email': 'testuser@example.com',
            'password': 'securepassword'
        }
        serializer = UserLoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

class FileListSerializerTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='securepassword',
            user_type='ops_user'
        )
        self.file = File.objects.create(
            file='path/to/testfile.docx', 
            uploaded_by=self.user
        )

    def test_file_list_serialization(self):
        serializer = FileListSerializer(self.file)
        expected_data = {
            'id': self.file.id,
            'file': self.file.file.url,
            'uploaded_by': str(self.user.email),
            'upload_date': self.file.upload_date.strftime("%Y-%m-%dT%H:%M:%S.%f") + 'Z'  # Adjust to match expected output
        }
        self.assertEqual(serializer.data, expected_data)
