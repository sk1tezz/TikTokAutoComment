import requests
from dotenv import dotenv_values

config = dotenv_values(".env")


def send_message(chat_id: int, text: str):
    url = f'https://api.telegram.org/bot{config["BOT_TOKEN"]}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }

    requests.post(url, data=payload)
