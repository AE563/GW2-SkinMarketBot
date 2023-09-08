# import requests
#
# ACCESS_TOKEN = \
#     '44718987-59DC-234C-AEFA-8491368222AF8DD722F7-0A84-4218-B2E8-AD56903D4503'
#
# current_sells_endpoint_mock = \
#     'http://0.0.0.0:8083/v2/commerce/transactions/history/sells_first'
#
# current_sells_endpoint = \
#     'https://api.guildwars2.com/v2/commerce/transactions/history/sells'
#
#
# query_params = {"access_token": ACCESS_TOKEN}
#
#
# response_mock = requests.get(current_sells_endpoint_mock, query_params)
# response_mock = response_mock.json()
#
# response_gw = requests.get(current_sells_endpoint, query_params)
# response_gw = response_gw.json()
#
# print(response_mock == response_gw)
