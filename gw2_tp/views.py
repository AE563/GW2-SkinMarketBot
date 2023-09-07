from django.shortcuts import render, redirect
from .models import *
from .gw2_tp import *


menu = [{'title': 'GitHub', 'url_name': 'github'},
        {'title': 'GW2-TP', 'url_name': 'gw2_tp'},
        {'title': 'RPSLS-game', 'url_name': 'rpsls_game'},
        ]


def gw2_tp(request):
    try:
        buys = Buys.objects.all()
    except Buys.DoesNotExist:
        buys = []  # Если данных нет, используем пустой список
    try:
        items = Items.objects.all()
    except Buys.DoesNotExist:
        items = []  # Если данных нет, используем пустой список

    context = {'menu': menu,
               'title': 'GW2-TP',
               'buys': buys,
               'items': items}
    return render(request, 'gw2_tp/gw2_tp.html', context=context)


def delete_all_entries(request):
    if request.method == 'POST':
        Buys.objects.all().delete()
        # Перенаправление на страницу после удаления
        return redirect('http://127.0.0.1:8000/gw2-tp/')
    return render(request, 'gw2_tp/gw2_tp.html')


def fetch_and_save_history_buys_gw2(request):
    fetch_and_save_history_buys()  # Запись в таблицу
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def fetch_items(request):
    update_items_table()
    return redirect('http://127.0.0.1:8000/gw2-tp/')
    # Перенаправьте на нужную страницу после выполнения операции


def delete_items(request):
    if request.method == 'POST':
        Items.objects.all().delete()
        # Перенаправление на страницу после удаления
        return redirect('http://127.0.0.1:8000/gw2-tp/')
    return render(request, 'gw2_tp/gw2_tp.html')

