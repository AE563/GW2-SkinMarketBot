from django.urls import path
from .views import *


urlpatterns = [
    path('main/', main, name='main'),
    path('notify/', time_to_notify, name='time_to_notify'),
    path('delete_all/', delete_all, name='delete_all'),
]
