from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('project/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/channel/<int:channel_id>/', views.channel_view, name='channel_view'),
    path('project/<int:project_id>/channel/add/', views.add_channel, name='add_channel'),
    path('project/<int:project_id>/channel/<int:channel_id>/delete/', views.delete_channel, name='delete_channel'),
    path('project/<int:project_id>/invite/', views.invite_member, name='invite_member'),
    path('project/<int:project_id>/member/<int:user_id>/remove/', views.remove_member, name='remove_member'),
    path('project/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    path('project/<int:project_id>/toggle-active/', views.toggle_project_active, name='toggle_project_active'),
    path('project/<int:project_id>/settings/', views.project_settings, name='project_settings'),
    path('join/<str:invite_code>/', views.join_by_invite, name='join_by_invite'),
]
