from django.contrib import admin
from .models import Message, DirectConversation

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender','content','channel','conversation','created_at')
    list_filter = ('is_deleted','is_edited')
    search_fields = ('content','sender__username')
