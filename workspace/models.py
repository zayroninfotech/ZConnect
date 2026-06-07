import secrets
from django.db import models
from accounts.models import User


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='💼')
    color = models.CharField(max_length=7, default='#7c5cbf')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    members = models.ManyToManyField(User, through='ProjectMember', related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    invite_code = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        db_table = 'zc_projects'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = secrets.token_urlsafe(12)
        super().save(*args, **kwargs)

    def get_member_role(self, user):
        try:
            return ProjectMember.objects.get(project=self, user=user).role
        except ProjectMember.DoesNotExist:
            return None

    def is_admin(self, user):
        return self.get_member_role(user) == 'admin' or self.created_by == user


class ProjectMember(models.Model):
    ROLES = [('admin', 'Admin'), ('member', 'Member'), ('viewer', 'Viewer')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, default='member', choices=ROLES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'zc_project_members'
        unique_together = ('project', 'user')


class Channel(models.Model):
    TYPES = [('text', 'Text'), ('voice', 'Voice')]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='channels')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, default='text', choices=TYPES)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_channels')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'zc_channels'
        ordering = ['type', 'name']

    def __str__(self):
        return f'{self.project.name} / #{self.name}'
