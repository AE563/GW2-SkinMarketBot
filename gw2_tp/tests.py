# @classmethod
# def calculate_and_update_selling_price(cls):
#     markup_percentage = 50  # Процент наценки. Например, 50% (1.5)
#     convert_markup_percentage_to_decimal_number = 1 + (markup_percentage / 100)
#     prices_to_update = cls.objects.filter(selling_price__isnull=True)
#     for price in prices_to_update:
#         selling_price = (price.price_now
#                          * convert_markup_percentage_to_decimal_number)
#         price.selling_price = selling_price
#         price.save()
