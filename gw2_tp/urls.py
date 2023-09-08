from django.urls import path
from .views import *


urlpatterns = [
    path('gw2-tp/', gw2_tp, name='gw2_tp'),
    path('get_history/', get_and_save_history_buys_gw2, name='get_history'),
    path('delete-entries/', delete_all_buys, name='delete_entries'),
    path('get_items/', get_items, name='get_items'),
    path('delete_items/', delete_items, name='delete_items'),
    path('get_items_prices/', get_items_prices, name='get_items_prices'),
    path('calculate_selling_price/', calculate_selling_price,
         name='calculate_selling_price'),
    path('get_current_sells_list/', get_current_sells_list,
         name='get_current_sells_list'),
    path('get_sells_data/', get_sells_data, name='get_sells_data'),
    path('delete_sells/', delete_sells, name='delete_sells'),

]
