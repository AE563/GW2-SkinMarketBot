debug = True
# debug = False


# Конечная точка API для получения данных истории покупок
if debug is True:
    # history_buys_endpoint = \
    #     'http://0.0.0.0:8083/v2/commerce/transactions/history/buy_first'

    history_buys_endpoint = \
        'http://0.0.0.0:8083/v2/commerce/transactions/history/buy_second'
else:
    history_buys_endpoint = \
        'https://api.guildwars2.com/v2/commerce/transactions/history/buys'


# Конечная точка API для получения данных текущих продаж
if debug is True:
    # current_sells_endpoint = \
    #     'http://0.0.0.0:8083/v2/commerce/transactions/current/sells_first'

    current_sells_endpoint = \
        'http://0.0.0.0:8083/v2/commerce/transactions/current/sells_second'
else:
    current_sells_endpoint = \
        'https://api.guildwars2.com/v2/commerce/transactions/current/sells'


# Конечная точка API для получения данных истории продаж
if debug is True:
    history_sells_endpoint = \
        'http://0.0.0.0:8083/v2/commerce/transactions/history/sells_first'

    # history_sells_endpoint = \
    #     'http://0.0.0.0:8083/v2/commerce/transactions/history/sells_second'
else:
    history_sells_endpoint = \
        'https://api.guildwars2.com/v2/commerce/transactions/history/sells'


# Токен доступа для аутентификации API
ACCESS_TOKEN = \
    '44718987-59DC-234C-AEFA-8491368222AF8DD722F7-0A84-4218-B2E8-AD56903D4503'


# Конечная точка API для получения данных о предметах
ITEMS_ENDPOINT = \
    'https://api.guildwars2.com/v2/items'

# Конечная точка API для получения данных о цене предмета
PRICE_ENDPOINT = 'https://api.guildwars2.com/v2/commerce/prices'
