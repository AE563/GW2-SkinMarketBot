from django.db import models
import requests
from gw2_tp.config import *
from django.db.models import Max


class BaseTransaction(models.Model):
    # ID транзакции, (десятичное число)
    transition_id = models.IntegerField(primary_key=True)
    # ID предмета, (десятичное число)
    item_id = models.IntegerField()
    # Цена, (десятичное число)
    price = models.IntegerField()
    # Количество, (десятичное число)
    quantity = models.IntegerField()
    # Дата размещения ордера (дата с временем)
    created = models.DateTimeField()

    class Meta:
        abstract = True  # Эта модель является абстрактной
        # и не будет создавать таблицу в базе данных.

    def __str__(self):
        return f"""
        ID: {self.transition_id}, 
        Item ID: {self.item_id}, 
        Price: {self.price}, 
        Quantity: {self.quantity}, 
        Created: {self.created}
        """

    @classmethod
    def check_api_response(cls, response):
        """
        Проверяет статус ответа API и возвращает данные в формате JSON,
        если статус успешный

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

    @classmethod
    def get_last_saved_transition_id(cls):
        """
        Получает максимальное значение transition_id из сохраненных записей

        Returns:
            int: Максимальное значение transition_id или None, если записей нет.
        """
        return cls.objects.aggregate(Max('transition_id'))['transition_id__max']

    @classmethod
    def save_entry(cls, entry):
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
        Получает данные о покупках из API.

        Returns:
            list: Список записей о покупках или пустой список, если произошла ошибка.
        """
        query_params = {"access_token": ACCESS_TOKEN}
        response = requests.get(endpoint, query_params)
        data = cls.check_api_response(response)
        return data

    @classmethod
    def get_and_save(cls, endpoint):
        """
        Получает данные о покупках из API и новые значения сохраняет в базе данных.

        Returns:
            None
        """
        last_saved_transition_id = cls.get_last_saved_transition_id()
        data = cls.get_trading_data(endpoint)

        if data is None:
            return

        for entry in data:
            transition_id = entry['id']

            if (last_saved_transition_id is None
                    or transition_id > last_saved_transition_id):
                cls.save_entry(entry)


class Buys(BaseTransaction):
    # Дата закрытия ордера (дата с временем)
    purchased = models.DateTimeField(blank=True, null=True)
    # Цена продажи (десятичное число)
    selling_price = models.IntegerField(blank=True, null=True)

    @classmethod
    def calculate_and_update_selling_price(cls):
        markup_percentage = 50  # Процент наценки. Например, 50% (1.5)
        convert_markup_percentage_to_decimal_number = 1 + (markup_percentage / 100)

        # Получаем все записи из таблицы Buys, у которых selling_price пустой (None)
        buys_to_update = cls.objects.filter(selling_price__isnull=True)

        for buy in buys_to_update:
            # Вычисляем selling_price с учетом наценки
            selling_price = (buy.price / buy.quantity
                             * convert_markup_percentage_to_decimal_number)
            # Обновляем запись с новым значением selling_price
            buy.selling_price = selling_price
            buy.save()  # Сохраняем изменения в базе данных


class CurrentSells(BaseTransaction):
    pass  # Эта модель наследует общие поля от BaseTransaction
    # и не добавляет своих дополнительных полей.


class Sells(BaseTransaction):
    # Дата закрытия ордера (дата с временем)
    purchased = models.DateTimeField(blank=True, null=True)


class Items(models.Model):
    # ID предмета (int)
    item_id = models.IntegerField(primary_key=True)
    # Название предмета (varchar)
    name = models.CharField(max_length=255, blank=True, null=True)
    # Описание предмета (varchar, пустое значение допустимо)
    description = models.CharField(max_length=255, blank=True, null=True)
    # Иконка предмета (varchar, пустое значение допустимо)
    icon = models.CharField(max_length=255, blank=True, null=True)
    # Статус предмета (boolean)
    sales_flag = models.BooleanField(default=False)
    # Остаток предмета (int)
    leftovers = models.IntegerField(default=0)
    # Является ли предмет скином для трансмутации (boolean)
    skin = models.BooleanField(default=True)
    # Цена сейчас (десятичное число)
    price_now = models.IntegerField(blank=True, null=True)
    # Максимальная цена за все время (десятичное число)
    maximum_price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"""
        ID: {self.item_id}, 
        Name: {self.name}, 
        Description: {self.description}, 
        Icon: {self.icon}, 
        Status ID: {self.sales_flag}, 
        Leftovers: {self.leftovers}, 
        Skin: {self.skin},
        Price now: {self.price_now},
        Maximum price: {self.maximum_price},
        """

    @classmethod
    def is_skin(cls, item_id):
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

    @classmethod
    def update_items_table(cls):
        """
        Обновляет таблицу Items данными о предметах, являющихся скинами для трансмутации

        Returns:
            None
        """
        # Получаем уникальные идентификаторы предметов из таблицы Buys
        unique_item_ids = Buys.objects.values('item_id').distinct()

        for item_info in unique_item_ids:
            item_id = item_info['item_id']
            if not cls.is_skin(item_id):
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
            cls.objects.update_or_create(item_id=item_id, defaults=item_defaults)

    def get_item_price(self):
        """
        Получает цену предмета по его идентификатору из API.

        Returns:
            float: Цена предмета.
        """
        query_params = {'ids': self.item_id}
        response = requests.get(PRICE_ENDPOINT, query_params)
        data_response = response.json()[0]
        item_price = data_response.get('sells').get('unit_price')
        return item_price

    def update_item_prices(self):
        """
        Обновляет цены на предметы и максимальные цены.

        Returns:
            None
        """
        # Получаем текущую цену продажи предмета
        current_price = self.get_item_price()
        self.price_now = current_price
        # Проверяем, является ли текущая цена максимальной
        if self.maximum_price is None or current_price > self.maximum_price:
            self.maximum_price = current_price

        self.save()
