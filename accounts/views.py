from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import User
from .forms import RegisterForm, ProfileForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me') == 'on'
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Your account has been disabled.')
                return render(request, 'accounts/login.html')
            login(request, user)

            # Remember me functionality - set session to persist for 30 days
            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days in seconds
                request.session['remember_me'] = True
            else:
                request.session.set_expiry(0)  # Browser session

            user.status = 'online'
            user.save(update_fields=['status'])
            next_url = request.GET.get('next', '/dashboard/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data.get('display_name'):
                user.display_name = form.cleaned_data['display_name']
            user.status = 'online'
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to ZayronConnect, {user.get_display_name()}!')
            return redirect('dashboard')
    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    if request.user.is_authenticated:
        request.user.status = 'offline'
        request.user.save(update_fields=['status'])
    logout(request)
    return redirect('login')


@login_required
def profile_view(request, username=None):
    profile_user = get_object_or_404(User, username=username) if username else request.user
    is_own = profile_user == request.user
    form = ProfileForm(instance=profile_user)

    if request.method == 'POST' and is_own:
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')

    # Common projects - safely handle missing relationships
    common_projects = []
    all_projects = []

    try:
        all_projects = list(request.user.projects.filter(is_active=True))
        if not is_own:
            my_projects = set(request.user.projects.values_list('id', flat=True))
            common_projects = list(profile_user.projects.filter(id__in=my_projects))
    except Exception:
        # If projects relationship doesn't exist yet, just show empty list
        all_projects = []
        common_projects = []

    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'form': form,
        'is_own': is_own,
        'common_projects': common_projects,
        'all_projects': all_projects,
    })


@login_required
def update_status(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['online', 'offline', 'busy', 'away']:
            request.user.status = status
            request.user.save(update_fields=['status'])
            return JsonResponse({'success': True, 'status': status, 'color': request.user.get_status_color()})
    return JsonResponse({'success': False}, status=400)


@login_required
def search_users(request):
    q = request.GET.get('q', '').strip()
    if len(q) >= 2:
        users = User.objects.filter(
            username__icontains=q
        ).exclude(id=request.user.id).values('id', 'username', 'display_name', 'status')[:10]
        data = []
        for u in users:
            data.append({
                'id': u['id'],
                'username': u['username'],
                'display_name': u['display_name'] or u['username'],
                'status': u['status'],
            })
        return JsonResponse({'users': data})
    return JsonResponse({'users': []})


# ─── Super Admin Panel ────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    if not (request.user.is_super_admin or request.user.is_staff):
        return redirect('dashboard')
    from workspace.models import Project
    context = {
        'total_users': User.objects.count(),
        'online_users': User.objects.filter(status='online').count(),
        'total_projects': Project.objects.filter(is_active=True).count(),
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'all_projects': request.user.projects.filter(is_active=True),
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def admin_users(request):
    if not (request.user.is_super_admin or request.user.is_staff):
        return redirect('dashboard')
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {
        'users': users,
        'all_projects': request.user.projects.filter(is_active=True),
    })


@login_required
def admin_toggle_user(request, user_id):
    if not (request.user.is_super_admin or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            return JsonResponse({'error': 'Cannot modify your own account'}, status=400)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return JsonResponse({'success': True, 'is_active': user.is_active})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def admin_make_admin(request, user_id):
    if not (request.user.is_super_admin or request.user.is_staff):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_super_admin = not user.is_super_admin
        user.save(update_fields=['is_super_admin'])
        return JsonResponse({'success': True, 'is_super_admin': user.is_super_admin})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ─── Super Admin: User Management ─────────────────────────────────────────────
@login_required
def super_admin_users(request):
    """Super Admin can create and manage all users (HR, Employee)"""
    if not request.user.is_super_admin_user():
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        display_name = request.POST.get('display_name', '').strip()
        role = request.POST.get('role', 'employee')
        email = request.POST.get('email', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                display_name=display_name,
                role=role,
                created_by=request.user,
                is_active=True
            )
            messages.success(request, f'{role.title()} {username} created successfully!')
            return redirect('super_admin_users')

    all_users = User.objects.exclude(id=request.user.id).order_by('-date_joined')
    super_admins = all_users.filter(role='super_admin').count()
    hrs = all_users.filter(role='hr').count()
    employees = all_users.filter(role='employee').count()

    return render(request, 'admin_panel/super_admin_users.html', {
        'users': all_users,
        'super_admins': super_admins,
        'hrs': hrs,
        'employees': employees,
    })


@login_required
def super_admin_edit_user(request, user_id):
    """Super Admin can edit user roles and permissions"""
    if not request.user.is_super_admin_user():
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'true'

        user.role = role
        user.is_active = is_active
        user.save()

        return JsonResponse({'success': True, 'message': f'User {user.username} updated'})

    return JsonResponse({'success': False}, status=400)


# ─── HR: Employee Management ──────────────────────────────────────────────────
@login_required
def hr_employees(request):
    """HR can create and manage employees"""
    if not request.user.is_hr_user():
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        display_name = request.POST.get('display_name', '').strip()
        email = request.POST.get('email', '').strip()

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
        else:
            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                display_name=display_name,
                role='employee',
                created_by=request.user,
                is_active=True
            )
            messages.success(request, f'Employee {username} created successfully!')
            return redirect('hr_employees')

    employees = User.objects.filter(created_by=request.user, role='employee').order_by('-date_joined')

    return render(request, 'admin_panel/hr_employees.html', {
        'employees': employees,
        'total_employees': employees.count(),
    })


@login_required
def user_management(request):
    """Superadmin user management - create and delete users"""
    if not request.user.is_super_admin:
        messages.error(request, 'Access denied. Superadmin only.')
        return redirect('dashboard')

    if request.method == 'POST' and 'create_user' in request.POST:
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        role = request.POST.get('role', 'employee')
        display_name = request.POST.get('display_name', '').strip()

        if not all([username, email, password, role]):
            messages.error(request, 'Please fill all required fields.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" already exists.')
        elif role not in ['hr', 'employee']:
            messages.error(request, 'Invalid role selected.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                display_name=display_name or username,
                role=role,
                created_by=request.user,
                is_active=True
            )
            messages.success(request, f'User {username} ({role.upper()}) created successfully!')
            return redirect('user_management')

    # Get all users except superadmin
    users = User.objects.exclude(role='super_admin').order_by('-date_joined')
    hr_users = users.filter(role='hr').count()
    employee_users = users.filter(role='employee').count()

    return render(request, 'accounts/user_management.html', {
        'users': users,
        'total_users': users.count(),
        'hr_count': hr_users,
        'employee_count': employee_users,
    })


@login_required
@require_POST
def delete_user(request, user_id):
    """Delete user from database"""
    if not request.user.is_super_admin:
        return JsonResponse({'success': False, 'message': 'Access denied.'})

    try:
        user = User.objects.get(id=user_id)
        if user.is_super_admin:
            return JsonResponse({'success': False, 'message': 'Cannot delete superadmin users.'})

        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('user_management')
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('user_management')
