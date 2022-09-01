import logging
import os
import time
from http import HTTPStatus
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    filemode='a',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5
)
logger.addHandler(handler)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logging.error(f'Не удалось отправить сообщение. {error}')
    else:
        logging.info('Сообщение отправлено')


def get_api_answer(current_timestamp):
    """Делает запрос к API-сервиса."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Статус ответа сервера:{response.status_code}')
    return response.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not (isinstance(response, dict)):
        raise TypeError('Ответ сервера не является словарем!')

    homeworks = response.get('homeworks')
    if not (isinstance(homeworks, list)):
        raise TypeError('homeworks не является списком!')

    if homeworks is None:
        raise KeyError('В ответе нет работ.')
    return homeworks


def parse_status(homework):
    """Извлекает статус домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        raise KeyError('Недокументированный статус домашней работы.')
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        logging.error('Отсутствие ключа homework_status или homework_name.')


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN))


def main():
    """Основная логика работы бота."""
    current_timestamp = 0
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    check = check_tokens()
    if not check:
        logging.critical('Недоступна переменная окружения.')
        raise ValueError('Функция check_tokens вернула False')

    while check:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if homeworks:
                message = parse_status(homeworks[0])
                send_message(bot, message)
            current_timestamp = response.get('current_date')
        except Exception as error:
            message_error = f'Сбой в работе программы: {error}'
            send_message(bot, message_error)
            logging.error(message_error)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
