import requests
from django.db.models import Max


from gw2_tp.models import Items, Buys, CurrentSells, Sells
from gw2_tp.config import *


def check_api_response(response):
    """
    Проверяет статус ответа API и возвращает данные в формате JSON, если статус успешный

    Args:
        response (requests.Response): Объект ответа API.

    Returns:
        dict: Данные в формате JSON, если ответ успешен, иначе None.
    """
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Ошибка при получении данных. Код ошибки: {response.status_code}")
        return None


def get_last_saved_transition_id(model):
    """
    Получает максимальное значение transition_id из сохраненных записей в базе данных.

    Args:
        model (models.Model): Модель, из которой нужно получить данные.

    Returns:
        int: Максимальное значение transition_id или None, если записей нет.
    """
    return model.objects.aggregate(Max('transition_id'))['transition_id__max']


def save_entry(entry, model):
    """
    Сохраняет запись о покупке в базе данных.

    Args:
        entry (dict): Запись о покупке.
        model (models.Model): Модель, в которую запишем данные.
    """
    transition_id = entry['id']
    item_id = entry['item_id']
    price = entry['price']
    quantity = entry['quantity']
    created = entry['created']

    model.objects.create(
        transition_id=transition_id,
        item_id=item_id,
        price=price,
        quantity=quantity,
        created=created,
    )


def get_trading_data(endpoint):
    """
    Получает данные о покупках из API.

    Returns:
        list: Список записей о покупках или пустой список, если произошла ошибка.
    """
    # data_fetch = []
    # pages = 0
    # query_params = {"access_token": ACCESS_TOKEN, "page_size": 200}
    # response = requests.get(endpoint, query_params)
    # max_pages = int(response.headers.get('X-Page-Total')) - 1
    #
    # while pages <= max_pages:
    #     pages += 1
    #     data_fetch += response.json()
    #     query_params = {"access_token": ACCESS_TOKEN, "page_size": 200, "page": pages}
    #     response = requests.get(endpoint, query_params)
    # return data_fetch
    query_params = {"access_token": ACCESS_TOKEN}
    response = requests.get(endpoint, query_params)
    data = check_api_response(response)
    return data


def get_and_save(endpoint, model):
    """
    Получает данные о покупках из API и новые значения сохраняет в базе данных.

    Returns:
        None
    """
    last_saved_transition_id = get_last_saved_transition_id(model)
    data = get_trading_data(endpoint)

    if data is None:
        return

    for entry in data:
        transition_id = entry['id']

        if last_saved_transition_id is None or transition_id > last_saved_transition_id:
            save_entry(entry, model)


def is_that_skin(item_id):
    """
    Проверяет, является ли предмет с указанным item_id скином для трансмутации.

    Args:
        item_id (int): ID предмета.

    Returns:
        bool: True, если предмет является скином для трансмутации, иначе False.
    """
    response = requests.get(ITEMS_ENDPOINT, {"ids": item_id})

    if response.status_code != 200:
        return False

    try:
        data = response.json()
        if data and isinstance(data, list):
            return data[0].get('details', {}).get('type') == 'Transmutation'
    except Exception as e:
        print(f"Ошибка при декодировании JSON: {e}")

    return False


def update_items_table():
    """
    Обновляет таблицу Items данными о предметах, являющихся скинами для трансмутации.

    Returns:
        None
    """
    # Получаем уникальные идентификаторы предметов из таблицы Buys
    unique_item_ids = Buys.objects.values('item_id').distinct()

    for item_info in unique_item_ids:
        item_id = item_info['item_id']
        if not is_that_skin(item_id):
            continue

        # Получаем данные о предмете из API
        response = requests.get(ITEMS_ENDPOINT, {"ids": item_id})
        item_data = response.json()

        # Устанавливаем значения по умолчанию для записи в таблице Items
        item_defaults = {
            'name': item_data[0]['name'],
            'description': item_data[0]['description'],
            'icon': item_data[0]['icon'],
            'sales_flag': False,
            'skin': True
        }

        # Обновляем или создаем запись в таблице Items
        Items.objects.update_or_create(item_id=item_id, defaults=item_defaults)


def calculate_and_update_selling_price():
    markup_percentage = 1.5  # Процент наценки

    # Получаем все записи из таблицы Buys, у которых selling_price пустой (None)
    buys_to_update = Buys.objects.filter(selling_price__isnull=True)

    for buy in buys_to_update:
        # Вычисляем selling_price с учетом наценки
        selling_price = buy.price / buy.quantity * markup_percentage
        # Обновляем запись с новым значением selling_price
        buy.selling_price = selling_price
        buy.save()  # Сохраняем изменения в базе данных


def get_item_price(item_id):
    """
    Получает цену предмета по его идентификатору из API.

    Args:
        item_id (int): Идентификатор предмета.

    Returns:
        float: Цена предмета.
    """
    query_params = {'ids': item_id}
    response = requests.get(PRICE_ENDPOINT, query_params)
    item_price = response.json()[0].get('sells').get('unit_price')
    return item_price


def update_item_prices():
    """
    Обновляет цены на предметы и максимальные цены в таблице Items.

    Returns:
        None
    """
    items = Items.objects.all()

    for item in items:
        # Получаем текущую цену продажи предмета
        current_price = get_item_price(item.item_id)
        item.price_now = current_price
        # Проверяем, является ли текущая цена максимальной
        if item.maximum_price is None or current_price > item.maximum_price:
            item.maximum_price = current_price

        item.save()
