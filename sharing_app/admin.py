from django.contrib import admin
from .models import User, File, VerificationToken
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_verified', 'user_type')  # Add user_type here
    list_filter = ('user_type', 'is_verified')  # Filter by user_type
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type',)}),  # Add user_type to the fieldsets
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type',)}),  # Add user_type to add_fieldsets
    )

# Register your models here
admin.site.register(User, CustomUserAdmin)  # Use CustomUserAdmin for User model
admin.site.register(File)
admin.site.register(VerificationToken)
