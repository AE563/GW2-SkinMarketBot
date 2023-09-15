from django.shortcuts import render, redirect
from gw2_tp.models import *
from gw2_tp.sending_notifications import notify


def gw2_tp_test(request):
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

    try:
        price = Price.objects.all()
    except Price.DoesNotExist:
        price = []  # Если данных нет, используем пустой список

    context = {'title': 'GW2-TP',
               'buys': buys,
               'items': items,
               'current_sells': current_sells,
               'sells': sells,
               'price': price}
    return render(request, 'gw2_tp/gw2_tp_test.html', context=context)


def get_and_save_buys(request):
    # Вызов функции для извлечения и сохранения истории покупок
    Buys.get_and_save(endpoint=history_buys_endpoint)
    return redirect('gw2-test')


def delete_all_buys(request):
    # Удаление всех записей о покупках
    Buys.objects.all().delete()
    return redirect('gw2-test')


def calculate_selling_price(request):
    # Вызов функции для обновления цен на предметы
    Price.calculate_and_update_selling_price()
    return redirect('gw2-test')


def get_items(request):
    # Вызов метода класса Items для обновления записей о предметах
    Items.update_items_table()
    return redirect('gw2-test')


def delete_items(request):
    # Удаление всех записей о предметах
    Items.objects.all().delete()
    return redirect('gw2-test')


def get_items_prices(request):
    # Получаем все объекты модели Items
    Price.update_or_create_prices_for_items()
    return redirect('gw2-test')


def get_current_sells_list(request):
    CurrentSells.objects.all().delete()
    CurrentSells.get_and_save(endpoint=current_sells_endpoint)
    return redirect('gw2-test')


def get_sells_data(request):
    # Вызов функции для извлечения и сохранения истории покупок
    Sells.get_and_save(endpoint=history_sells_endpoint)
    return redirect('gw2-test')


def delete_sells(request):
    # Удаление всех записей о предметах
    Sells.objects.all().delete()
    return redirect('gw2-test')


def get_leftovers(request):
    calculate_and_update_leftovers()
    return redirect('gw2-test')


def time_to_notify(request):
    notify()
    return redirect('gw2-test')


def main(request):
    empty_list = []

    # Попытка получить все записи о покупках
    try:
        buys = Buys.objects.all()
    except Buys.DoesNotExist:
        buys = empty_list  # Если данных нет, используем пустой список

    # Попытка получить все записи о предметах
    try:
        items = Items.objects.all()
    except Items.DoesNotExist:
        items = empty_list  # Если данных нет, используем пустой список

    # Попытка получить все записи о предметах на продаже
    try:
        current_sells = CurrentSells.objects.all()
    except CurrentSells.DoesNotExist:
        current_sells = empty_list  # Если данных нет, используем пустой список

    try:
        sells = Sells.objects.all()
    except Sells.DoesNotExist:
        sells = empty_list  # Если данных нет, используем пустой список

    try:
        price = Price.objects.all()
    except Price.DoesNotExist:
        price = empty_list  # Если данных нет, используем пустой список

    context = {'title': 'GW2-TP',
               'buys': buys,
               'items': items,
               'current_sells': current_sells,
               'sells': sells,
               'price': price}
    return render(request, 'gw2_tp/main.html', context=context)
