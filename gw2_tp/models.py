from django.db import models
import requests
from gw2_tp.config import *
from django.db.models import Max, Sum


class BaseTransaction(models.Model):
    transition_id = models.IntegerField(primary_key=True)
    item_id = models.IntegerField()
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
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Ошибка при получении данных. Код ошибки: {response.status_code}")
            return None

    @classmethod
    def get_last_saved_transition_id(cls):
        return cls.objects.aggregate(Max('transition_id'))['transition_id__max']

    @classmethod
    def save_entry(cls, entry):
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
        if debug is True:
            query_params = {"access_token": ACCESS_TOKEN}
            response = requests.get(endpoint, query_params)
            data = cls.check_api_response(response)
            return data

        else:
            data_fetch = []
            pages = 0
            query_params = {"access_token": ACCESS_TOKEN, "page_size": 200}
            response = requests.get(endpoint, query_params)
            max_pages = int(response.headers.get('X-Page-Total')) - 1

            while pages <= max_pages:
                pages += 1
                data_fetch += response.json()
                query_params = {"access_token": ACCESS_TOKEN,
                                "page_size": 200,
                                "page": pages}
                response = requests.get(endpoint, query_params)
            return data_fetch

    @classmethod
    def get_and_save(cls, endpoint):
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
    purchased = models.DateTimeField(blank=True, null=True)


class CurrentSells(BaseTransaction):
    pass


class Sells(BaseTransaction):
    purchased = models.DateTimeField(blank=True, null=True)


class Items(models.Model):
    item_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)
    skin = models.BooleanField(default=True)

    def __str__(self):
        return (f"ID: {self.item_id}, "
                f"Name: {self.name}, "
                f"Description: {self.description}, "
                f"Icon: {self.icon}, "
                f"Skin: {self.skin}, ")

    @classmethod
    def is_skin(cls, item_id):
        if Items.objects.filter(item_id=item_id).exists():
            return True

        response = requests.get(ITEMS_ENDPOINT, {"ids": item_id})

        if response.status_code != 200:
            return False

        try:
            data = response.json()
            if data and isinstance(data, list):
                return data[0].get('details', {}).get('type') == 'Transmutation'
        except Exception as error:
            print(f"Ошибка при декодировании JSON: {error}")

        return False

    @classmethod
    def update_items_table(cls):
        unique_item_ids = Buys.objects.values('item_id').distinct()

        for item_info in unique_item_ids:
            item_id = item_info['item_id']
            if not cls.is_skin(item_id):
                continue

            response = requests.get(ITEMS_ENDPOINT, {"ids": item_id})
            item_data = response.json()

            item_defaults = {
                'name': item_data[0]['name'],
                'description': item_data[0]['description'],
                'icon': item_data[0]['icon'],
                'skin': True
            }

            cls.objects.update_or_create(item_id=item_id, defaults=item_defaults)

    def is_eligible_for_sale(self):
        """
        Проверяет, является ли предмет подходящим для продажи.

        Returns:
            bool: True, если предмет подходит для продажи, иначе False.
        """
        # Проверка на наличие остатков
        currently_available = Leftovers.objects.get(item_id=self)

        if currently_available.currently_available <= 0:
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


class Leftovers(models.Model):
    item_id = models.ForeignKey(Items, on_delete=models.CASCADE, default=None)
    currently_available = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'''{self.currently_available}'''


def calculate_and_update_leftovers():
    unique_item_ids = Items.objects.values('item_id').distinct()
    for item_info in unique_item_ids:
        item_id = item_info['item_id']
        total_buys = (Buys.objects
                      .filter(item_id=item_id)
                      .aggregate(Sum('quantity'))['quantity__sum'] or 0)
        total_buys = total_buys or 0  # Если сумма пуста (нет покупок), устанавливаем 0
        total_sells = (Sells.objects
                       .filter(item_id=item_id)
                       .aggregate(Sum('quantity'))['quantity__sum'] or 0)
        total_sells = total_sells or 0  # Если сумма пуста (нет продаж), устанавливаем 0
        leftovers_value = total_buys - total_sells

        # Получить экземпляр Items по item_id
        item_instance, created = Items.objects.get_or_create(item_id=item_id)

        # Получить или создать запись Leftovers, используя экземпляр Items
        leftovers_instance, leftovers_created = Leftovers.objects.get_or_create(
            item_id=item_instance,
            defaults={'currently_available': leftovers_value}
        )

        if not leftovers_created:
            leftovers_instance.currently_available = leftovers_value
            leftovers_instance.save()


class Price(models.Model):
    item_id = models.ForeignKey(Items, on_delete=models.CASCADE, default=None)
    selling_price = models.IntegerField(blank=True, null=True)
    price_now = models.IntegerField(blank=True, null=True)
    maximum_price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"""
        Item ID: {self.item_id},
        Selling Price: {self.selling_price},
        Price Now: {self.price_now},
        Maximum Price: {self.maximum_price}
        """

    @classmethod
    def calculate_and_update_selling_price(cls):
        markup_percentage = 50  # Процент наценки. Например, 50% (1.5)
        percentage_to_decimal_number = 1 + (markup_percentage / 100)
        unique_item_ids = Items.objects.values('item_id').distinct()

        for item_info in unique_item_ids:
            counter = 0
            item_id = item_info['item_id']
            data = Leftovers.objects.get(item_id=item_id)
            currently_available = data.currently_available

            buys = (Buys.objects.filter(item_id=item_id).order_by('-transition_id'))
            for buy in buys:
                quantity = buy.quantity
                counter += quantity
                if counter >= currently_available:
                    price_buy = buy.price
                    quantity_buy = buy.quantity
                    price_per_item = price_buy / quantity_buy
                    selling_price = price_per_item * percentage_to_decimal_number
                    price_instance = cls.objects.get(item_id=item_id)
                    price_instance.selling_price = selling_price
                    price_instance.save()
                    break

    @classmethod
    def update_or_create_prices_for_items(cls):
        unique_item_ids = Items.objects.values('item_id').distinct()
        for item_info in unique_item_ids:
            item_id = item_info['item_id']
            try:
                price_instance = cls.objects.get(item__item_id=item_id)
            except cls.DoesNotExist:
                price_instance = None
            if not price_instance:
                price_instance = cls(item=Items.objects.get(item_id=item_id))
            query_params = {'ids': item_id}
            response = requests.get(PRICE_ENDPOINT, query_params)
            data_response = response.json()[0]
            item_price = data_response.get('sells').get('unit_price')
            price_instance.price_now = item_price
            if (price_instance.maximum_price is None
                    or item_price > price_instance.maximum_price):
                price_instance.maximum_price = item_price

            price_instance.save()
