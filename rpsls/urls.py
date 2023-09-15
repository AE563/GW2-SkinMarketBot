from django.urls import path
from . import views

urlpatterns = [
    path('rpsls/', views.rpsls_game, name='rpsls'),
]
