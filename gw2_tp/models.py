import requests
from django.db import models
from gw2_tp.config import *
from django.db.models import Max, Sum
from gw2_tp.tokens import GW_API_ACCESS_KEY


def get_unique_item_ids(*data_lists):
    """
    Получает уникальные item_id из нескольких списков данных.

    Args:
        *data_lists (list): Списки данных, из которых нужно извлечь уникальные item_id.

    Returns:
        list: Список уникальных item_id.
    """
    unique_item_ids_set = set()

    for data_list in data_lists:
        for item_data in data_list:
            item_id = item_data['item_id']
            unique_item_ids_set.add(item_id)

    return list(unique_item_ids_set)


class Items(models.Model):
    item_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, default='')
    description = models.CharField(max_length=255, default='')
    icon = models.CharField(max_length=255, default='')
    skin = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return (f"ID: {self.item_id}, "
                f"Name: {self.name}, "
                f"Description: {self.description}, "
                f"Icon: {self.icon}, "
                f"Skin: {self.skin}, ")

    @classmethod
    def update_items_table(cls, unique_item_ids):
        """
        Обновляет таблицу предметов (Items) на основе списка уникальных item_id.

        Args:
            unique_item_ids (list): Список уникальных item_id, которые нужно обновить.

        Notes:
            Метод выполняет запрос к API
             для получения информации о предметах на основе их item_id.
            Затем метод обновляет
            или создает записи в таблице Items на основе полученных данных.

        Returns:
            None
        """
        item_ids_to_update = []

        # TODO: Сделать обработку более 200+ запросов

        for item_id in unique_item_ids:
            # Проверьте, есть ли предмет уже в таблице
            if not cls.objects.filter(item_id=item_id).exists():
                item_ids_to_update.append(item_id)

        if (not item_ids_to_update) or (item_ids_to_update == []):
            return

        response = requests.get(ITEMS_ENDPOINT,
                                {"ids": ",".join(map(str, item_ids_to_update))})
        if response.status_code != 200:
            return

        try:
            data = response.json()
            for item_data in data:
                item_id = item_data['id']
                item_defaults = {
                    'name': item_data.get('name', ''),
                    'description': item_data.get('description', ''),
                    'icon': item_data.get('icon', ''),
                    'skin': item_data.get('details', {}).get('type') == 'Transmutation'
                }
                cls.objects.update_or_create(item_id=item_id, defaults=item_defaults)
        except Exception as error:
            print(f"Ошибка при декодировании JSON: {error}")

    def is_eligible_for_sale(self):
        """
        Проверяет, является ли предмет подходящим для продажи.

        Returns:
            bool: True, если предмет подходит для продажи, иначе False.
        """
        # Проверка, является ли предмет скином
        if self.skin != 1:
            return False

        # Проверка на наличие остатков
        try:
            leftovers = Leftovers.objects.get(item_id=self)
            currently_available = leftovers.currently_available

            if currently_available <= 0:
                return False
        except Leftovers.DoesNotExist:
            # Если записи в таблице Leftovers нет, то предмет не подходит для продажи
            return False

        # Проверка на отсутствие в таблице CurrentSells
        if CurrentSells.objects.filter(item_id=self.item_id).exists():
            return False

        # Получение цены продажи из таблицы Price
        try:
            price = Price.objects.get(item_id=self)
            if price.price_now < price.selling_price:
                return False
        except Price.DoesNotExist:
            # Если записи в таблице Price нет, то предмет не подходит для продажи
            return False

        # Если все условия выполнены, предмет подходит для продажи
        return True


class BaseTransaction(models.Model):
    transition_id = models.IntegerField(primary_key=True)
    item = models.ForeignKey(Items, on_delete=models.CASCADE, default=None)
    price = models.IntegerField()
    quantity = models.IntegerField()
    created = models.DateTimeField()

    class Meta:
        abstract = True

    def __str__(self):
        return (f"ID: {self.transition_id}, "
                f"Item ID: {self.item_id}, "
                f"Price: {self.price}, "
                f"Quantity: {self.quantity}, "
                f"Created: {self.created}")

    @classmethod
    def check_api_response(cls, response):
        """
        Проверяет ответ от API и возвращает данные из него, если ответ успешен.

        Args:
            response: Ответ от API.

        Returns:
            list: Данные из ответа, если успешно, или None в случае ошибки.
        """
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Ошибка при получении данных. Код ошибки: {response.status_code}")
            return None

    @classmethod
    def get_last_saved_transition_id(cls):
        """
        Получает последний сохраненный идентификатор перехода (transition_id).

        Returns:
            int: Последний сохраненный transition_id или None, если нет данных.
        """
        return cls.objects.aggregate(Max('transition_id'))['transition_id__max']

    @classmethod
    def save_entry(cls, entry):
        """
        Сохраняет запись о переходе в базе данных.

        Args:
            entry (dict): Информация о переходе, содержащая поля
            'id', 'item_id', 'price', 'quantity', 'created'.
        """
        transition_id = entry['id']
        item_id = entry['item_id']
        price = entry['price']
        quantity = entry['quantity']
        created = entry['created']

        cls.objects.create(
            transition_id=transition_id,
            item_id=item_id,
            price=price,
            quantity=quantity,
            created=created,
        )

    @classmethod
    def get_trading_data(cls, endpoint):
        """
        Получает данные торговли (trading data)
         из API, предоставляемого по указанному `endpoint`.

        Args:
            endpoint (str): URL-адрес API-конечной точки для получения данных торговли.

        Returns:
            list: Список данных торговли.
        """
        access_token = GW_API_ACCESS_KEY
        page_size = 200
        page = 0
        if debug:
            # Если включен режим отладки, делаем запрос без пагинации
            query_params = {"access_token": access_token}
            response = requests.get(endpoint, query_params)
            data = cls.check_api_response(response)
            return data
        else:
            data_fetch = []
            query_params = {"access_token": access_token, "page_size": page_size}
            response = requests.get(endpoint, query_params)
            max_pages = int(response.headers.get('X-Page-Total')) - 1

            # Перебираем страницы с данными
            while page <= max_pages:
                page += 1
                data_fetch += response.json()
                query_params = {"access_token": access_token,
                                "page_size": 200,
                                "page": page}
                response = requests.get(endpoint, query_params)

            return data_fetch

    @classmethod
    def get_and_save(cls, data):
        """
        Получает данные `data` и сохраняет их, если `transition_id`
         в данных больше, чем `last_saved_transition_id`.

        Args:
            data (list): Список данных для сохранения.

        Returns:
            None
        """
        last_saved_transition_id = cls.get_last_saved_transition_id()

        if data is None:
            return

        for entry in data:
            transition_id = entry['id']

            if (last_saved_transition_id is None
                    or transition_id > last_saved_transition_id):
                cls.save_entry(entry)


class Buys(BaseTransaction):
    purchased = models.DateTimeField(blank=True, null=True)


class CurrentSells(BaseTransaction):
    pass


class Sells(BaseTransaction):
    purchased = models.DateTimeField(blank=True, null=True)


class Leftovers(models.Model):
    item = models.ForeignKey(Items, on_delete=models.CASCADE, default=None)
    currently_available = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return f'''{self.currently_available}'''


def calculate_and_update_leftovers():
    """
    Рассчитывает и обновляет остатки для предметов, у которых skin=True.

    Returns:
        None
    """
    # Получить все item_id, для которых скин = 1
    skin_item_ids = Items.objects.filter(skin=True).values('item_id')

    for item_info in skin_item_ids:
        item_id = item_info['item_id']

        # Рассчитать остатки только для предметов, скин которых = 1
        total_buys = (Buys.objects
                      .filter(item_id=item_id)
                      .aggregate(Sum('quantity'))['quantity__sum'] or 0)
        total_buys = total_buys or 0  # Если сумма пуста (нет покупок), устанавливаем 0
        total_sells = (Sells.objects
                       .filter(item_id=item_id)
                       .aggregate(Sum('quantity'))['quantity__sum'] or 0)
        total_sells = total_sells or 0  # Если сумма пуста (нет продаж), устанавливаем 0
        leftovers_value = total_buys - total_sells

        # Получить или создать запись Leftovers, используя item_id
        leftovers_instance, leftovers_created = Leftovers.objects.get_or_create(
            item_id=item_id,
            defaults={'currently_available': leftovers_value}
        )

        if not leftovers_created:
            leftovers_instance.currently_available = leftovers_value
            leftovers_instance.save()


class Price(models.Model):
    item = models.ForeignKey(Items, on_delete=models.CASCADE, default=None)
    selling_price = models.IntegerField(blank=True, default=0)
    price_now = models.IntegerField(blank=True, default=0)
    maximum_price = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return f"""
        Item ID: {self.item},
        Selling Price: {self.selling_price},
        Price Now: {self.price_now},
        Maximum Price: {self.maximum_price}
        """

    @classmethod
    def calculate_and_update_selling_price(cls):
        """
        Рассчитывает и обновляет цены на продажу для предметов на основе наценки
        и истории покупок.

        Returns:
            None
        """
        markup_percentage = 75  # Процент наценки. Например, 75% (1.75)
        percentage_to_decimal_number = 1 + (markup_percentage / 100)

        # Получаем все item_id, для которых skin=True
        skin_item_ids = Items.objects.filter(skin=True).values('item_id').distinct()

        # Собираем все item_id для одного запроса
        # TODO вынести это отдельной функцией
        item_ids_to_update = [item_info['item_id'] for item_info in skin_item_ids]
        query_params = {'ids': ",".join(map(str, item_ids_to_update))}
        response = requests.get(PRICE_ENDPOINT, query_params)
        data_response = response.json()

        selling_prices = {}

        for item_data in data_response:
            item_id = item_data['id']
            currently_available = Leftovers.objects.get(
                item_id=item_id).currently_available

            buys = Buys.objects.filter(item_id=item_id).order_by('-transition_id')
            counter = 0

            for buy in buys:
                quantity = buy.quantity
                counter += quantity

                if counter >= currently_available:
                    price_buy = buy.price
                    quantity_buy = buy.quantity
                    price_per_item = price_buy / quantity_buy
                    selling_price = price_per_item * percentage_to_decimal_number
                    selling_prices[item_id] = selling_price
                    break

        for item_id, selling_price in selling_prices.items():
            try:
                price_instance = cls.objects.get(item__item_id=item_id)
            except cls.DoesNotExist:
                price_instance = None

            if not price_instance:
                price_instance = cls(item=Items.objects.get(item_id=item_id))

            price_instance.selling_price = selling_price
            price_instance.save()

    @classmethod
    def update_or_create_prices_for_items(cls):
        """
        Обновляет или создает цены для предметов,
        у которых цена продажи отсутствует и skin=True.

        Returns:
            None
        """
        # Получаем все item_id, для которых цена продажи отсутствует и skin=True
        # TODO перепроверить функцию
        unique_item_ids = Items.objects.filter(price__isnull=True, skin=True).values(
            'item_id').distinct()

        # Собираем все item_id для одного запроса
        # TODO вынести это отдельной функцией
        item_ids_to_update = [item_info['item_id'] for item_info in unique_item_ids]
        if not item_ids_to_update:
            return

        query_params = {'ids': ','.join(map(str, item_ids_to_update))}
        response = requests.get(PRICE_ENDPOINT, query_params)
        data_response = response.json()

        selling_prices = {}

        for item_data in data_response:
            item_id = item_data['id']
            item_price = item_data['sells']['unit_price']
            selling_prices[item_id] = item_price

        for item_id in item_ids_to_update:
            try:
                price_instance = cls.objects.get(item__item_id=item_id)
            except cls.DoesNotExist:
                price_instance = cls(item=Items.objects.get(item_id=item_id))

            item_price = selling_prices.get(item_id)
            if item_price is not None:
                price_instance.price_now = item_price

            if (price_instance.maximum_price is None
                    or (
                            item_price is not None
                            and item_price > price_instance.maximum_price)):
                price_instance.maximum_price = item_price

            price_instance.save()
