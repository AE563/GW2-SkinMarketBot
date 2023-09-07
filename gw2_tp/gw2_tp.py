import requests
from django.db.models import Max


from .models import *
from .config import *


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


def get_last_saved_transition_id():
    """
    Получает максимальное значение transition_id из сохраненных записей в базе данных.

    Returns:
        int: Максимальное значение transition_id или None, если записей нет.
    """
    return Buys.objects.aggregate(Max('transition_id'))['transition_id__max']


def save_gw2tp_buy_entry(entry):
    """
    Сохраняет запись о покупке в базе данных.

    Args:
        entry (dict): Запись о покупке.
    """
    transition_id = entry['id']
    item_id = entry['item_id']
    price = entry['price']
    quantity = entry['quantity']
    created = entry['created']
    purchased = entry['purchased']

    Buys.objects.create(
        transition_id=transition_id,
        item_id=item_id,
        price=price,
        quantity=quantity,
        created=created,
        purchased=purchased
    )


def fetch_gw2tp_buys_data():
    """
    Получает данные о покупках из API.

    Returns:
        list: Список записей о покупках или пустой список, если произошла ошибка.
    """
    query_params = {"access_token": ACCESS_TOKEN, "page_size": 1}
    if DEBUG is True:
        query_params.pop('DEBUG', 1)
    response = requests.get(HISTORY_BUYS_ENDPOINT, query_params)
    print(response.headers.get('X-Page-Total'))
    data = check_api_response(response)
    return data


fetch_gw2tp_buys_data()


def fetch_and_save_history_buys():
    """
    Получает данные о покупках из API и новые значения сохраняет в базе данных.

    Returns:
        None
    """
    last_saved_transition_id = get_last_saved_transition_id()
    data = fetch_gw2tp_buys_data()

    if data is None:
        return

    for entry in data:
        transition_id = entry['id']

        if last_saved_transition_id is None or transition_id > last_saved_transition_id:
            save_gw2tp_buy_entry(entry)


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
    unique_item_ids = Buys.objects.values('item_id').distinct()

    for item_info in unique_item_ids:
        item_id = item_info['item_id']
        if not is_that_skin(item_id):
            continue

        response = requests.get(ITEMS_ENDPOINT, {"ids": item_id})
        item_data = response.json()

        item_defaults = {
            'name': item_data[0]['name'],
            'description': item_data[0]['description'],
            'icon': item_data[0]['icon'],
            'status_id': True,
            'skin': True
        }

        Items.objects.update_or_create(item_id=item_id, defaults=item_defaults)
