from django.urls import path
from . import views

urlpatterns = [
    path('rpsls/', views.rpsls_game, name='rpsls'),
    path('make-choice/', views.make_choice, name='make-choice'),
]
