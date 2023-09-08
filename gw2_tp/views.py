from django.shortcuts import render, redirect
from .gw2_tp import *
from gw2_tp.config import *


menu = [{'title': 'GitHub', 'url_name': 'github'},
        {'title': 'GW2-TP', 'url_name': 'gw2_tp'},
        {'title': 'RPSLS-game', 'url_name': 'rpsls_game'},
        ]


def gw2_tp(request):
    # Попытка получить все записи о покупках
    try:
        buys = Buys.objects.all()
    except Buys.DoesNotExist:
        buys = []  # Если данных нет, используем пустой список

    # Попытка получить все записи о предметах
    try:
        items = Items.objects.all()
    except Items.DoesNotExist:
        items = []  # Если данных нет, используем пустой список

    # Попытка получить все записи о предметах на продаже
    try:
        current_sells = CurrentSells.objects.all()
    except CurrentSells.DoesNotExist:
        current_sells = []  # Если данных нет, используем пустой список

    try:
        sells = Sells.objects.all()
    except Sells.DoesNotExist:
        sells = []  # Если данных нет, используем пустой список

    context = {'menu': menu,
               'title': 'GW2-TP',
               'buys': buys,
               'items': items,
               'current_sells': current_sells,
               'sells': sells}
    return render(request, 'gw2_tp/gw2_tp.html', context=context)


def delete_all_buys(request):
    # Удаление всех записей о покупках
    Buys.objects.all().delete()
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def get_and_save_history_buys_gw2(request):
    # Вызов функции для извлечения и сохранения истории покупок
    get_and_save(endpoint=history_buys_endpoint, model=Buys)
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def get_items(request):
    # Вызов функции для обновления записей о предметах
    update_items_table()
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def delete_items(request):
    # Удаление всех записей о предметах
    Items.objects.all().delete()
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def get_items_prices(request):
    # Вызов функции для обновления цен на предметы
    update_item_prices()
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def calculate_selling_price(request):
    # Вызов функции для обновления цен на предметы
    calculate_and_update_selling_price()
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def get_current_sells_list(request):
    CurrentSells.objects.all().delete()
    get_and_save(endpoint=current_sells_endpoint, model=CurrentSells)
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def get_sells_data(request):
    # Вызов функции для извлечения и сохранения истории покупок
    get_and_save(endpoint=history_sells_endpoint, model=Sells)
    return redirect('http://127.0.0.1:8000/gw2-tp/')


def delete_sells(request):
    # Удаление всех записей о предметах
    Sells.objects.all().delete()
    return redirect('http://127.0.0.1:8000/gw2-tp/')
