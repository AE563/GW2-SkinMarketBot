from django.urls import path
from .views import *


urlpatterns = [
    path('gw2-tp/', gw2_tp, name='gw2_tp'),
    path('fetch-history/', fetch_and_save_history_buys_gw2, name='fetch_history'),
    path('delete-entries/', delete_all_entries, name='delete_entries'),
]