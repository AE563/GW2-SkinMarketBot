from django.shortcuts import render, redirect

from gw2_tp.gw2_update_and_alert import data_update
from gw2_tp.models import *
from gw2_tp.sending_notifications import notify
from django.db.models import Sum, CharField, Value


def main(request):
    path_info = request.META.get('PATH_INFO')
    http_host = request.META.get('HTTP_HOST')

    summary_data = []
    empty_list = []

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
    items_info = Items.objects.filter(item_id__in=item_ids)

    context = {
        'title': 'GW2-TP',
        'summary_data': summary_data,
        'items_info': items_info,
    }

    return render(request, 'gw2_tp/main.html', context=context)


def delete_all(request):
    Buys.objects.all().delete()
    Sells.objects.all().delete()
    CurrentSells.objects.all().delete()
    # Items.objects.all().delete()
    Price.objects.all().delete()
    Leftovers.objects.all().delete()
    return redirect('main')


def time_to_notify(request):
    data_update()
    notify()
    return redirect('main')
