# DEBUG = True
DEBUG = False


# Конечная точка API для получения данных истории транзакций
HISTORY_BUYS_ENDPOINT = \
    'https://api.guildwars2.com/v2/commerce/transactions/history/buys'
if DEBUG is True:
    HISTORY_BUYS_ENDPOINT = \
        'http://0.0.0.0:8083/v2/commerce/transactions/history/buy'

# Конечная точка API для получения данных о предметах
ITEMS_ENDPOINT = \
    'https://api.guildwars2.com/v2/items'
if DEBUG is True:
    ITEMS_ENDPOINT = \
        'http://0.0.0.0:8083/v2/items'


# Токен доступа для аутентификации API
ACCESS_TOKEN = \
    '44718987-59DC-234C-AEFA-8491368222AF8DD722F7-0A84-4218-B2E8-AD56903D4503'
