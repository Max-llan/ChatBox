from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('send/', views.send_message, name='send_message'),
    path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('history/', views.get_emotional_history, name='emotional_history'),
    path('statistics/', views.get_statistics, name='statistics'),
]
