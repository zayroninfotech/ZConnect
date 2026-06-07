from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    path('status/update/', views.update_status, name='update_status'),
    path('api/users/search/', views.search_users, name='search_users'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/<int:user_id>/toggle/', views.admin_toggle_user, name='admin_toggle_user'),
    path('admin-panel/users/<int:user_id>/make-admin/', views.admin_make_admin, name='admin_make_admin'),

    # Super Admin - User Management
    path('super-admin/users/', views.super_admin_users, name='super_admin_users'),
    path('super-admin/users/<int:user_id>/edit/', views.super_admin_edit_user, name='super_admin_edit_user'),

    # HR - Employee Management
    path('hr/employees/', views.hr_employees, name='hr_employees'),
]
