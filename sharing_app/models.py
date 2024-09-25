from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure email is unique
    USER_TYPE_CHOICES = (
        ('ops_user', 'Ops User'),
        ('client_user', 'Client User'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)  # User type
    is_verified = models.BooleanField(default=False)  # Email verification status
    username = models.CharField(max_length=150, unique=False)  # Allow non-unique usernames

    USERNAME_FIELD = 'email'  # Set the USERNAME_FIELD to email
    REQUIRED_FIELDS = ['username']  # Add any other required fields

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class File(models.Model):
    file = models.FileField(upload_to='uploads/')  # Store uploaded files
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    upload_date = models.DateTimeField(default=timezone.now)  # Auto-set upload date

class VerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to User
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)  # Unique token
    created_at = models.DateTimeField(default=timezone.now)  # Token creation timestamp
    expiry_date = models.DateTimeField()  # Expiry date for the token

    def save(self, *args, **kwargs):
        if not self.id:
            # Set expiry date to 24 hours from creation
            self.expiry_date = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        # Check if the token has expired
        return timezone.now() > self.expiry_date
