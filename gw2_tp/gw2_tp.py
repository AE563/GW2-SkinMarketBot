import requests
from django.db.models import Max


from .models import Gw2tpBuys
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
    return Gw2tpBuys.objects.aggregate(Max('transition_id'))['transition_id__max']


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

    Gw2tpBuys.objects.create(
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
    query_params = {"access_token": ACCESS_TOKEN}
    response = requests.get(HISTORY_BUYS_ENDPOINT, query_params)
    data = check_api_response(response)
    return data


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
    response_items = requests.get(ITEMS_ENDPOINT, {"ids": item_id}).json()
    data = response_items[0].get('details')
    if data is None:
        # Если детали предмета отсутствуют, возвращаем False
        return False
    if data.get('type') == 'Transmutation':
        return True
    return False  # Возвращаем False по умолчанию, если тип не 'Transmutation'
