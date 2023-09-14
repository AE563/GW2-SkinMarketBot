import requests
from gw2_tp.tokens import TG_BOT_TOKEN, TG_CHAT_ID


def send_text(text):
    url = f'https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': TG_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=data)

    # Проверяем успешность запроса
    if response.status_code == 200:
        print('Сообщение успешно отправлено в Telegram.')
    else:
        print(
            f'Ошибка при отправке сообщения в Telegram. '
            f'Код ошибки: {response.status_code}')
