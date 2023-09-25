import os

from django.core.wsgi import get_wsgi_application
from concurrent.futures import ThreadPoolExecutor

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


# Настройка окружения Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ae563_site.settings")
application = get_wsgi_application()


def data_update():
    """
    Обновляет данные о транзакциях, предметах и ценах.

    Эта функция запрашивает данные о покупках, продажах и текущих продажах,
    обновляет список предметов, сохраняет транзакции, обновляет остатки и цены.

    Returns:
        None
    """
    # Запрашиваем дату по всем покупкам, продажам за последние 90 дней
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

    # Получили список уникальных item_id для обновления списка предметов
    unique_item_ids = get_unique_item_ids(data_buys,
                                          data_current_sells, data_sells)

    # Обновляем список предметов
    Items.update_items_table(unique_item_ids)

    # Обновляем покупки
    Buys.get_and_save(data=data_buys)

    # Обновляем предметы на продаже
    CurrentSells.objects.all().delete()
    CurrentSells.get_and_save(data=data_current_sells)

    # Обновляем проданное
    Sells.get_and_save(data=data_sells)

    # Обновляем остатки
    calculate_and_update_leftovers()

    # Обновляем актуальные цены
    Price.update_or_create_prices_for_items()

    # Обновляем цены продажи
    Price.calculate_and_update_selling_price()

    return
