from django.contrib import admin
from .models import Call, CallParticipant


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'initiator', 'call_type', 'status', 'started_at')
    list_filter = ('status', 'call_type')
