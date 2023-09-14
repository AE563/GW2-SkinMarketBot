import requests

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш настоящий токен Telegram бота
TOKEN = '5759952619:AAGzguveLyOFmiyjHLOVvcZUkl9O-x-gmvQ'
CHAT_ID = -847535892


def send_text(text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': CHAT_ID,
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
