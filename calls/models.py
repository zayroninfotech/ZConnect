import uuid
from django.db import models
from accounts.models import User
from workspace.models import Channel

class Call(models.Model):
    STATUS = [('waiting','Waiting'),('active','Active'),('ended','Ended')]
    TYPES = [('video','Video'),('audio','Audio')]
    room_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_calls')
    participants = models.ManyToManyField(User, through='CallParticipant', related_name='calls')
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.SET_NULL, related_name='calls')
    call_type = models.CharField(max_length=20, default='video', choices=TYPES)
    status = models.CharField(max_length=20, default='waiting', choices=STATUS)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'zc_calls'

class CallParticipant(models.Model):
    call = models.ForeignKey(Call, on_delete=models.CASCADE, related_name='call_participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'zc_call_participants'
        unique_together = ('call','user')
