from django.urls import path
from . import views

urlpatterns = [
    path('call/start/', views.start_call, name='start_call'),
    path('call/<str:room_id>/', views.call_room, name='call_room'),
    path('call/<str:room_id>/end/', views.end_call, name='end_call'),
]
