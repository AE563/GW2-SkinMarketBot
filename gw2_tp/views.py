from django.shortcuts import render, redirect
from django.db.models import CharField, Value

from gw2_tp.gw2_update_and_alert import data_update
from gw2_tp.models import *
from gw2_tp.sending_notifications import notify


def main(request):
    """
    Основная функция для отображения сводной информации о покупках, продажах и предметах

    Args:
        request (HttpRequest): Запрос от клиента.

    Returns:
        HttpResponse: Ответ с отображаемой информацией.
    """
    summary_data = []
    empty_list = []

    # Получаем сводную информацию о покупках, продажах и предметах
    for source, category in [(Buys, 'Покупки'),
                             (CurrentSells, 'Сейчас на продаже'),
                             (Sells, 'Продано')]:
        try:
            data = source.objects.filter(item_id__skin=True).values(
                'item_id', 'price', 'quantity'
            ).annotate(
                total_price=Sum('price'),
                total_quantity=Sum('quantity'),
                category=Value(category, output_field=CharField())
            ).order_by('item_id__name')
        except source.DoesNotExist:
            data = empty_list

        unique_item_ids = data.values_list('item_id', flat=True).distinct()

        for item_id in unique_item_ids:
            total_price = data.filter(item_id=item_id).aggregate(
                total_price=Sum('price'))['total_price']
            total_quantity = data.filter(item_id=item_id).aggregate(
                total_quantity=Sum('quantity'))['total_quantity']

            summary_data.append({
                'item_id': item_id,
                'total_price': total_price,
                'total_quantity': total_quantity,
                'category': category,
            })

    item_ids = [entry['item_id'] for entry in summary_data]

    # Получаем информацию о предметах
    items_info = Items.objects.filter(item_id__in=item_ids)

    context = {
        'title': 'GW2-TP',
        'summary_data': summary_data,
        'items_info': items_info,
    }

    # Отправляем ответ с отображаемой информацией
    return render(request, 'gw2_tp/gw2_alert_main.html', context=context)


def delete_all(request):
    """
    Очищает данные из различных моделей в базе данных
    и перенаправляет на главную страницу.

    Args:
        request (HttpRequest): Запрос от клиента.

    Returns:
        HttpResponseRedirect: Перенаправление на главную страницу.
    """
    # Удаляем все записи из модели Buys
    Buys.objects.all().delete()

    # Удаляем все записи из модели Sells
    Sells.objects.all().delete()

    # Удаляем все записи из модели CurrentSells
    CurrentSells.objects.all().delete()

    # Удаляем все записи из модели Price
    Price.objects.all().delete()

    # Удаляем все записи из модели Leftovers
    Leftovers.objects.all().delete()

    # Удаляем все записи из модели Items
    # Items.objects.all().delete()

    # Перенаправляем пользователя на главную страницу
    return redirect('main')


def time_to_notify(request):
    """
    Вызывает обновление данных и отправку уведомлений,
    а затем перенаправляет на главную страницу.

    Args:
        request (HttpRequest): Запрос от клиента.

    Returns:
        HttpResponseRedirect: Перенаправление на главную страницу.
    """
    # Вызываем функцию обновления данных
    data_update()

    # Вызываем функцию отправки уведомлений
    notify()

    # Перенаправляем пользователя на главную страницу
    return redirect('main')
