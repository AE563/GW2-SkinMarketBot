from django.db import models


class Gw2tpBuys(models.Model):
    transition_id = models.IntegerField()  # ID транзакции, (десятичное число)
    item_id = models.IntegerField()        # ID предмета, (десятичное число)
    price = models.IntegerField()          # Цена, (десятичное число)
    quantity = models.IntegerField()       # Количество, (десятичное число)
    created = models.DateTimeField()       # Дата размещения ордера (дата с временем)
    purchased = models.DateTimeField()     # Дата закрытия ордера (дата с временем)

    def __str__(self):
        return f"""
        ID: {self.transition_id}, 
        Item ID: {self.item_id}, 
        Price: {self.price}, 
        Quantity: {self.quantity}, 
        Created: {self.created}, 
        Purchased: {self.purchased}"""
