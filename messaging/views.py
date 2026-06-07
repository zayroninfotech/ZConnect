import mimetypes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from accounts.models import User
from .models import Message, DirectConversation

@login_required
def get_or_create_dm(request, user_id):
    other = get_object_or_404(User, id=user_id)
    conv = DirectConversation.objects.filter(participants=request.user).filter(participants=other).first()
    if not conv:
        conv = DirectConversation.objects.create()
        conv.participants.add(request.user, other)
    return redirect('dm_view', conv_id=conv.id)

@login_required
def dm_view(request, conv_id):
    conv = get_object_or_404(DirectConversation, id=conv_id, participants=request.user)
    other = conv.get_other(request.user)
    msgs = Message.objects.filter(conversation=conv).select_related('sender').order_by('created_at')[:50]
    raw_dms = DirectConversation.objects.filter(participants=request.user).order_by('-updated_at')[:15]
    all_dms = [{'conv': c, 'other': c.get_other(request.user)} for c in raw_dms if c.get_other(request.user)]
    return render(request, 'messaging/dm_view.html', {
        'conv': conv, 'other_user': other, 'messages': msgs,
        'all_dms': all_dms, 'all_projects': request.user.projects.filter(is_active=True),
    })

@login_required
def upload_file(request, room_type, room_id):
    if request.method != 'POST' or not request.FILES.get('file'):
        return JsonResponse({'error': 'No file'}, status=400)
    file = request.FILES['file']
    if file.size > 52428800:
        return JsonResponse({'error': 'File too large (max 50MB)'}, status=400)
    file_type, _ = mimetypes.guess_type(file.name)
    file_type = file_type or 'application/octet-stream'
    if room_type == 'channel':
        from workspace.models import Channel
        channel = get_object_or_404(Channel, id=room_id)
        if not channel.project.members.filter(id=request.user.id).exists():
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        msg = Message.objects.create(channel=channel, sender=request.user, file=file, file_name=file.name, file_size=file.size, file_type=file_type)
    elif room_type == 'dm':
        conv = get_object_or_404(DirectConversation, id=room_id, participants=request.user)
        msg = Message.objects.create(conversation=conv, sender=request.user, file=file, file_name=file.name, file_size=file.size, file_type=file_type)
        conv.save()
    else:
        return JsonResponse({'error': 'Invalid type'}, status=400)
    return JsonResponse({'success': True, 'data': msg.to_dict()})

@login_required
def load_messages(request, room_type, room_id):
    before_id = request.GET.get('before')
    if room_type == 'channel':
        qs = Message.objects.filter(channel_id=room_id)
    elif room_type == 'dm':
        qs = Message.objects.filter(conversation_id=room_id, conversation__participants=request.user)
    else:
        return JsonResponse({'messages': []})
    if before_id:
        qs = qs.filter(id__lt=before_id)
    msgs = [m.to_dict() for m in qs.select_related('sender').order_by('-created_at')[:20]]
    return JsonResponse({'messages': list(reversed(msgs))})
