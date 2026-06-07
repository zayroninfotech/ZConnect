from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    STATUS_CHOICES = [('online','Online'),('offline','Offline'),('busy','Busy'),('away','Away')]
    display_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_super_admin = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='offline', choices=STATUS_CHOICES)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    class Meta:
        db_table = 'zc_users'
    def get_display_name(self):
        return self.display_name or self.get_full_name() or self.username
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        colors = ['#7c5cbf','#e74c3c','#3498db','#2ecc71','#e67e22','#9b59b6']
        color = colors[self.id % len(colors)] if self.id else '#7c5cbf'
        initial = (self.get_display_name() or 'U')[0].upper()
        return f'/static/img/default_avatar.svg?color={color[1:]}&letter={initial}'
    def get_status_color(self):
        return {'online':'#23a55a','offline':'#80848e','busy':'#f23f43','away':'#f0b232'}.get(self.status,'#80848e')
    def get_initials(self):
        name = self.get_display_name()
        parts = name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return name[:2].upper() if name else 'U'
