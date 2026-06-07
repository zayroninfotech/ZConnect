from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'display_name', 'status', 'is_super_admin', 'is_active', 'date_joined')
    list_filter = ('status', 'is_super_admin', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'display_name')
    fieldsets = UserAdmin.fieldsets + (
        ('ZConnect Profile', {'fields': ('display_name', 'avatar', 'is_super_admin', 'status', 'bio', 'phone')}),
    )
