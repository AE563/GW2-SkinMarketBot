# from django.test import TestCase

# Create your tests here.
# def fetch_and_save_history_buys_gw2():
#     access_token = \
#         '44718987-59DC-234C-AEFA-8491368222AF8DD722F7-0A84-4218-B2E8-AD56903D4503'
#     history_buys_endpoint = \
#         'https://api.guildwars2.com/v2/commerce/transactions/history/buys'
#
#     try:
#         query_params_gw = {"access_token": access_token}
#         # Выполняем GET-запрос к API с помощью requests
#         response = requests.get(history_buys_endpoint, query_params_gw)
#
#         # Проверяем статус ответа API с помощью функции check_api_response
#         data = check_api_response(response)
#         if data:
#             # Проходим по данным и сохраните их в базу данных
#             for entry in data:
#                 transition_id = entry['id']
#                 item_id = entry['item_id']
#                 price = entry['price']
#                 quantity = entry['quantity']
#                 created = entry['created']
#                 purchased = entry['purchased']
#
#                 # Создайте объект Gw2tpBuys и сохраните его в базу данных
#                 Gw2tpBuys.objects.create(transition_id=transition_id,
#                                          item_id=item_id,
#                                          price=price,
#                                          quantity=quantity,
#                                          created=created,
#                                          purchased=purchased,)
#
#     except requests.exceptions.RequestException as error:
#         # Обработка ошибки при выполнении запроса
#         print(f"Ошибка при выполнении запроса к API: {error}")