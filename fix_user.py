#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zconnect.settings')
django.setup()

from accounts.models import User

# Check if user exists
user = User.objects.filter(username='vamsi').first()

if user:
    print("User found:", user.username)
    print("Is Active:", user.is_active)

    # Reset password to be sure
    user.set_password('zayron@2026')
    user.is_active = True
    user.save()
    print("Password updated to: zayron@2026")

    if user.check_password('zayron@2026'):
        print("Password verification: SUCCESS")
    else:
        print("Password verification: FAILED")
else:
    print("User not found. Creating new user...")
    user = User.objects.create_superuser(
        username='vamsi',
        email='vamsi@zayronconnect.tech',
        password='zayron@2026'
    )
    user.is_active = True
    user.save()
    print("User created successfully!")
    print("Username: vamsi")
    print("Password: zayron@2026")
