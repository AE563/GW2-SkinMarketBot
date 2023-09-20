import os
from django.core.wsgi import get_wsgi_application
from concurrent.futures import ThreadPoolExecutor
import time

from .config import (history_buys_endpoint,
                     current_sells_endpoint,
                     history_sells_endpoint)
from .models import (BaseTransaction,
                     get_unique_item_ids,
                     Items,
                     Buys,
                     CurrentSells,
                     Sells,
                     calculate_and_update_leftovers,
                     Price)
from .sending_notifications import notify

# Настройка окружения Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ae563_site.settings")
application = get_wsgi_application()


def data_update():
    start_time = time.time()
    # Запрашиваем дату по всем покупкам \ продажам \ за последние 90 дней
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Запускаем каждый запрос в отдельном потоке
        future_buys = executor.submit(BaseTransaction.get_trading_data,
                                      endpoint=history_buys_endpoint)
        future_current_sells = executor.submit(BaseTransaction.get_trading_data,
                                               endpoint=current_sells_endpoint)
        future_sells = executor.submit(BaseTransaction.get_trading_data,
                                       endpoint=history_sells_endpoint)

        data_buys = future_buys.result()
        data_current_sells = future_current_sells.result()
        data_sells = future_sells.result()
    end_time1 = time.time()
    execution_time1 = end_time1 - start_time
    print(execution_time1)

    # Получили список уникальных item_id для обновления списка предметов
    print('Получили список уникальных item_id для обновления списка предметов - Start')
    unique_item_ids = get_unique_item_ids(data_buys,
                                          data_current_sells, data_sells)
    print('Получили список уникальных item_id для обновления списка предметов - END')

    # Обновляем список предметов
    print('Обновляем список предметов - Start')
    Items.update_items_table(unique_item_ids)
    print('Обновляем список предметов - END')

    # Обновляем покупки
    print('Обновляем покупки - Start')
    Buys.get_and_save(data=data_buys)
    print('Обновляем покупки - END')

    # Обновляем предметы на продаже
    print('Обновляем предметы на продаже - Start')
    CurrentSells.objects.all().delete()
    CurrentSells.get_and_save(data=data_current_sells)
    print('Обновляем предметы на продаже - END')

    # Обновляем проданное
    print('Обновляем проданное - Start')
    Sells.get_and_save(data=data_sells)
    print('Обновляем проданное - END')

    # Обновляем остатки
    print('Обновляем остатки - Start')
    calculate_and_update_leftovers()
    print('Обновляем остатки - END')

    # Обновляем актуальные цены
    print('Обновляем актуальные цены - Start')
    Price.update_or_create_prices_for_items()
    print('Обновляем актуальные цены - END')

    # Обновляем цены продажи
    print('Обновляем цены продажи - Start')
    Price.calculate_and_update_selling_price()
    print('Обновляем цены продажи - END')

    end_time2 = time.time()
    execution_time2 = end_time2 - start_time
    print(execution_time2)
    return
