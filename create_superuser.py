"""
Run this once to create the super admin account:
  python create_superuser.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zconnect.settings')
django.setup()

from accounts.models import User

username = input("Super admin username [admin]: ").strip() or "admin"
email    = input("Email [admin@zconnect.local]: ").strip() or "admin@zconnect.local"
password = input("Password [Admin@123]: ").strip() or "Admin@123"

if User.objects.filter(username=username).exists():
    print(f"User '{username}' already exists.")
else:
    u = User.objects.create_superuser(username=username, email=email, password=password)
    u.is_super_admin = True
    u.display_name   = "Super Admin"
    u.save()
    print(f"\n✅ Super admin '{username}' created!")
    print(f"   Login at http://127.0.0.1:8000/login/")
