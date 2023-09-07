from django.db import models


class Buys(models.Model):
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
    # Дата закрытия ордера (дата с временем)
    purchased = models.DateTimeField()
    # Цена продажи (десятичное число)
    selling_price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"""
        ID: {self.transition_id}, 
        Item ID: {self.item_id}, 
        Price: {self.price}, 
        Quantity: {self.quantity}, 
        Created: {self.created}, 
        Purchased: {self.purchased},
        Selling price: {self.selling_price}
        """


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
    status_id = models.BooleanField(default=True)
    # Остаток предмета (int)
    leftovers = models.IntegerField(default=0)
    # Является ли предмет скином для трансмутации (boolean)
    skin = models.BooleanField(default=True)

    def __str__(self):
        return f"""
        ID: {self.item_id}, 
        Name: {self.name}, 
        Description: {self.description}, 
        Icon: {self.icon}, 
        Status ID: {self.status_id}, 
        Leftovers: {self.leftovers}, 
        Skin: {self.skin}
        """
