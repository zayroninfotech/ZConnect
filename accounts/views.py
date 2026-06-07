from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User
from .forms import RegisterForm, ProfileForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        password = request.POST.get('password','')
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Your account has been disabled.')
                return render(request, 'accounts/login.html')
            login(request, user)
            user.status = 'online'
            user.save(update_fields=['status'])
            return redirect(request.GET.get('next', '/dashboard/'))
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
            messages.success(request, f'Welcome to ZConnect, {user.get_display_name()}!')
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
    common_projects = []
    if not is_own:
        my_projects = set(request.user.projects.values_list('id', flat=True))
        common_projects = profile_user.projects.filter(id__in=my_projects)
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user, 'form': form, 'is_own': is_own,
        'common_projects': common_projects,
        'all_projects': request.user.projects.filter(is_active=True),
    })

@login_required
def update_status(request):
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in ['online','offline','busy','away']:
            request.user.status = status
            request.user.save(update_fields=['status'])
            return JsonResponse({'success':True,'status':status,'color':request.user.get_status_color()})
    return JsonResponse({'success':False}, status=400)

@login_required
def search_users(request):
    q = request.GET.get('q','').strip()
    if len(q) >= 2:
        users = User.objects.filter(username__icontains=q).exclude(id=request.user.id).values('id','username','display_name','status')[:10]
        data = [{'id':u['id'],'username':u['username'],'display_name':u['display_name'] or u['username'],'status':u['status']} for u in users]
        return JsonResponse({'users': data})
    return JsonResponse({'users': []})

@login_required
def admin_dashboard(request):
    if not (request.user.is_super_admin or request.user.is_staff):
        return redirect('dashboard')
    from workspace.models import Project
    return render(request, 'admin_panel/dashboard.html', {
        'total_users': User.objects.count(),
        'online_users': User.objects.filter(status='online').count(),
        'total_projects': Project.objects.filter(is_active=True).count(),
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'all_projects': request.user.projects.filter(is_active=True),
    })

@login_required
def admin_users(request):
    if not (request.user.is_super_admin or request.user.is_staff):
        return redirect('dashboard')
    return render(request, 'admin_panel/users.html', {
        'users': User.objects.all().order_by('-date_joined'),
        'all_projects': request.user.projects.filter(is_active=True),
    })

@login_required
def admin_toggle_user(request, user_id):
    if not (request.user.is_super_admin or request.user.is_staff):
        return JsonResponse({'error':'Unauthorized'}, status=403)
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user == request.user:
            return JsonResponse({'error':'Cannot modify your own account'}, status=400)
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        return JsonResponse({'success':True,'is_active':user.is_active})
    return JsonResponse({'error':'Method not allowed'}, status=405)

@login_required
def admin_make_admin(request, user_id):
    if not (request.user.is_super_admin or request.user.is_staff):
        return JsonResponse({'error':'Unauthorized'}, status=403)
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.is_super_admin = not user.is_super_admin
        user.save(update_fields=['is_super_admin'])
        return JsonResponse({'success':True,'is_super_admin':user.is_super_admin})
    return JsonResponse({'error':'Method not allowed'}, status=405)
