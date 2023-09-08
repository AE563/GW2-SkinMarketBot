from django.db import models


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


class Buys(BaseTransaction):
    # Дата закрытия ордера (дата с временем)
    purchased = models.DateTimeField(blank=True, null=True)
    # Цена продажи (десятичное число)
    selling_price = models.IntegerField(blank=True, null=True)


class CurrentSells(BaseTransaction):
    pass  # Эта модель наследует общие поля от BaseTransaction
    # и не добавляет своих дополнительных полей.


class Sells(BaseTransaction):
    # Дата закрытия ордера (дата с временем)
    purchased = models.DateTimeField(blank=True, null=True)
