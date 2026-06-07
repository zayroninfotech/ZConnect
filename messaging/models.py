from django.db import models
from accounts.models import User
from workspace.models import Channel

class DirectConversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'zc_conversations'
    def get_other(self, user):
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    conversation = models.ForeignKey(DirectConversation, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True)
    file = models.FileField(upload_to='attachments/%Y/%m/', null=True, blank=True)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(default=0)
    file_type = models.CharField(max_length=100, blank=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'zc_messages'
        ordering = ['created_at']
    def is_image(self):
        return self.file_type.startswith('image/') if self.file_type else False
    def format_file_size(self):
        size = self.file_size
        for unit in ['B','KB','MB','GB']:
            if size < 1024:
                return f'{size:.0f} {unit}'
            size /= 1024
        return f'{size:.1f} TB'
    def to_dict(self):
        d = {
            'id': self.id,
            'content': self.content if not self.is_deleted else '[Message deleted]',
            'sender_id': self.sender_id,
            'sender_name': self.sender.get_display_name(),
            'sender_avatar': self.sender.get_avatar_url(),
            'sender_initials': self.sender.get_initials(),
            'timestamp': self.created_at.strftime('%H:%M'),
            'date': self.created_at.strftime('%Y-%m-%d'),
            'is_edited': self.is_edited,
            'is_deleted': self.is_deleted,
            'file': None,
        }
        if self.file and not self.is_deleted:
            d['file'] = {'url': self.file.url, 'name': self.file_name, 'size': self.format_file_size(), 'type': self.file_type, 'is_image': self.is_image()}
        return d
