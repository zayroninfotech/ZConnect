import uuid
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Call, CallParticipant
from workspace.models import Channel

@login_required
def start_call(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    call_type = request.POST.get('type','video')
    channel_id = request.POST.get('channel_id')
    room_id = str(uuid.uuid4())
    call = Call.objects.create(room_id=room_id, initiator=request.user, call_type=call_type)
    if channel_id:
        try:
            call.channel = Channel.objects.get(id=channel_id)
            call.save()
        except Channel.DoesNotExist:
            pass
    CallParticipant.objects.get_or_create(call=call, user=request.user)
    return JsonResponse({'success': True, 'room_id': room_id, 'redirect': f'/call/{room_id}/'})

@login_required
def call_room(request, room_id):
    try:
        call = Call.objects.get(room_id=room_id)
        if call.status == 'ended':
            return render(request, 'calls/ended.html', {'all_projects': request.user.projects.filter(is_active=True)})
        CallParticipant.objects.get_or_create(call=call, user=request.user)
        if call.status == 'waiting':
            call.status = 'active'
            call.save(update_fields=['status'])
    except Call.DoesNotExist:
        call = None
    return render(request, 'calls/room.html', {
        'room_id': room_id, 'call': call,
        'call_type': call.call_type if call else 'video',
        'my_id': request.user.id,
        'my_name': request.user.get_display_name(),
        'my_initials': request.user.get_initials(),
        'all_projects': request.user.projects.filter(is_active=True),
    })

@login_required
def end_call(request, room_id):
    if request.method == 'POST':
        try:
            call = Call.objects.get(room_id=room_id)
            if call.initiator == request.user or request.user.is_super_admin:
                call.status = 'ended'
                call.ended_at = timezone.now()
                call.save(update_fields=['status','ended_at'])
        except Call.DoesNotExist:
            pass
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'POST required'}, status=405)
