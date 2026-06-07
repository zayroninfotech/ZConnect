from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import User
from .models import Project, ProjectMember, Channel


@login_required
def dashboard(request):
    projects = request.user.projects.filter(is_active=True).order_by('-created_at')
    from messaging.models import DirectConversation
    raw_dms = DirectConversation.objects.filter(participants=request.user).order_by('-updated_at')[:8]
    dms = [{'conv': c, 'other': c.get_other(request.user)} for c in raw_dms if c.get_other(request.user)]
    return render(request, 'workspace/dashboard.html', {
        'projects': projects,
        'dms': dms,
        'all_projects': projects,
    })


@login_required
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        icon = request.POST.get('icon', '💼')
        color = request.POST.get('color', '#7c5cbf')
        if not name:
            return JsonResponse({'error': 'Project name is required'}, status=400)
        project = Project.objects.create(
            name=name, description=description,
            icon=icon, color=color, created_by=request.user,
        )
        ProjectMember.objects.create(project=project, user=request.user, role='admin')
        Channel.objects.create(project=project, name='general', type='text', created_by=request.user)
        Channel.objects.create(project=project, name='announcements', type='text', created_by=request.user)
        Channel.objects.create(project=project, name='General Voice', type='voice', created_by=request.user)
        return JsonResponse({'success': True, 'redirect': f'/project/{project.id}/'})
    return render(request, 'workspace/create_project.html', {
        'all_projects': request.user.projects.filter(is_active=True),
    })


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, is_active=True)
    if not project.members.filter(id=request.user.id).exists():
        return redirect('dashboard')
    channels = project.channels.all()
    first_channel = channels.filter(type='text').first()
    if first_channel:
        return redirect('channel_view', project_id=project_id, channel_id=first_channel.id)
    return render(request, 'workspace/project_detail.html', _project_context(request, project, None))


@login_required
def channel_view(request, project_id, channel_id):
    project = get_object_or_404(Project, id=project_id, is_active=True)
    channel = get_object_or_404(Channel, id=channel_id, project=project)
    if not project.members.filter(id=request.user.id).exists():
        return redirect('dashboard')
    if channel.type == 'voice':
        return render(request, 'calls/voice_channel.html', _project_context(request, project, channel))
    from messaging.models import Message
    msgs = Message.objects.filter(channel=channel).select_related('sender').order_by('created_at')[:50]
    ctx = _project_context(request, project, channel)
    ctx['messages'] = msgs
    return render(request, 'workspace/channel_view.html', ctx)


def _project_context(request, project, channel):
    channels = project.channels.all()
    members = project.members.select_related().all()
    member_roles = {pm.user_id: pm.role for pm in project.memberships.all()}
    return {
        'project': project,
        'channel': channel,
        'text_channels': channels.filter(type='text'),
        'voice_channels': channels.filter(type='voice'),
        'members': members,
        'member_roles': member_roles,
        'member_role': project.get_member_role(request.user),
        'all_projects': request.user.projects.filter(is_active=True),
    }


@login_required
def add_channel(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not project.is_admin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip().lower().replace(' ', '-')
        ch_type = request.POST.get('type', 'text')
        if not name:
            return JsonResponse({'error': 'Channel name required'}, status=400)
        ch = Channel.objects.create(project=project, name=name, type=ch_type, created_by=request.user)
        return JsonResponse({'success': True, 'channel': {'id': ch.id, 'name': ch.name, 'type': ch.type}})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def delete_channel(request, project_id, channel_id):
    project = get_object_or_404(Project, id=project_id)
    channel = get_object_or_404(Channel, id=channel_id, project=project)
    if not project.is_admin(request.user):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if request.method == 'POST':
        channel.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def invite_member(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not project.is_admin(request.user):
        return JsonResponse({'error': 'Only admins can invite'}, status=403)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        if project.members.filter(id=user.id).exists():
            return JsonResponse({'error': 'User already in project'}, status=400)
        ProjectMember.objects.create(project=project, user=user, role='member')
        return JsonResponse({'success': True, 'message': f'{user.get_display_name()} added!'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def remove_member(request, project_id, user_id):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(User, id=user_id)
    if not (project.is_admin(request.user) or request.user.id == user_id):
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    if user == project.created_by:
        return JsonResponse({'error': 'Cannot remove project creator'}, status=400)
    if request.method == 'POST':
        ProjectMember.objects.filter(project=project, user=user).delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def join_by_invite(request, invite_code):
    project = get_object_or_404(Project, invite_code=invite_code, is_active=True)
    if not project.members.filter(id=request.user.id).exists():
        ProjectMember.objects.create(project=project, user=request.user, role='member')
    return redirect('project_detail', project_id=project.id)


@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, created_by=request.user)
    if request.method == 'POST':
        project.is_active = False
        project.save()
        return JsonResponse({'success': True, 'redirect': '/dashboard/'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def project_settings(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if not project.is_admin(request.user):
        return redirect('project_detail', project_id=project_id)
    if request.method == 'POST':
        project.name = request.POST.get('name', project.name).strip()
        project.description = request.POST.get('description', project.description).strip()
        project.icon = request.POST.get('icon', project.icon)
        project.color = request.POST.get('color', project.color)
        project.save()
        return JsonResponse({'success': True})
    ctx = _project_context(request, project, None)
    return render(request, 'workspace/project_settings.html', ctx)
