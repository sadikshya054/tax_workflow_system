from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


# Registers our custom User model in the Django admin panel.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Adds the custom role field to the user edit page.
    fieldsets = UserAdmin.fieldsets + (
        ('System Role', {'fields': ('role',)}),
    )

    # Adds the role field when creating a new user.
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('System Role', {'fields': ('role',)}),
    )