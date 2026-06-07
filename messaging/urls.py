from django.urls import path
from . import views

urlpatterns = [
    path('dm/<int:user_id>/', views.get_or_create_dm, name='start_dm'),
    path('messages/dm/<int:conv_id>/', views.dm_view, name='dm_view'),
    path('upload/<str:room_type>/<int:room_id>/', views.upload_file, name='upload_file'),
    path('messages/load/<str:room_type>/<int:room_id>/', views.load_messages, name='load_messages'),
]
