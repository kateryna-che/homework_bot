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
    filemode='a'
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
        logging.info('Сообщение отправлено')
    except Exception as error:
        logging.error(f'Не удалось отправить сообщение. {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к API-сервиса."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if response.status_code != HTTPStatus.OK:
        raise Exception(f'Статус ответа сервера:{response.status_code}')
    response = response.json()
    return response


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not (isinstance(response, dict)):
        logger.error('Ответ сервера не является словарем!')
        raise TypeError('Ответ сервера не является словарем!')

    try:
        homeworks = response['homeworks']
        if not (isinstance(homeworks, list)):
            logger.error('homeworks не является списком!')
            raise TypeError('homeworks не является списком!')
        return homeworks
    except Exception as error:
        logging.error(f'Отсутствие ожидаемых ключей в ответе API.{error}')
        raise


def parse_status(homework):
    """Извлекает статус домашней работы."""
    homework_name = homework['homework_name']
    homework_status = homework['status']

    verdicts = {
        'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
        'reviewing': 'Работа взята на проверку ревьюером.',
        'rejected': 'Работа проверена: у ревьюера есть замечания.'
    }
    try:
        verdict = verdicts[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except Exception as error:
        logging.error(f'Недокументированный статус домашней работы.{error}')
        raise


def check_tokens():
    """Проверяет доступность переменных окружения."""
    try:
        if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID is not None:
            return True
    except Exception as error:
        logging.critical(f'Недоступна переменная окружения. {error}')
    return False


def main():
    """Основная логика работы бота."""
    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    check_tokens()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            for i in range(len(homeworks)):
                message = parse_status(homeworks[i])
                send_message(bot, message)

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
