import json
import logging
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import requests
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    filename="../logs/utils.log",
    filemode="w",
)

utils_logger = logging.getLogger("utils")


def get_data_from_date(user_date_time_str: str) -> pd.DataFrame:
    '''Возвращает отфильтрованный список транзакций в зависимости от полученной даты'''
    utils_logger.info('Старт работы функции get_data_from_date')
    file_name = '../data/operations.xlsx'
    user_period_data = pd.DataFrame({})
    try:
        utils_logger.info('Переводим дату в текстовом формате в формат дат')
        user_date_time = datetime.strptime(user_date_time_str, "%d-%m-%Y %H:%M:%S")

        utils_logger.info('Получаем операции из файла для дальнейшей обработки')
        excel_data = pd.read_excel(file_name)
        utils_logger.info('Фильтруем операции от первого дня месяца введенной даты до введенной даты')
        excel_data['Дата операции'] = pd.to_datetime(excel_data['Дата операции'], dayfirst=True)
        user_period_data = excel_data[
            (excel_data['Дата операции'].between(user_date_time.replace(day=1), (user_date_time + timedelta(days=1))))]
        utils_logger.info('Возвращаем полученные операции')
        return user_period_data
    except Exception:
        utils_logger.error(f'Что-то пошло не так с {file_name}')
        return user_period_data


def get_currency_and_stock() -> json:
    '''Возвращает список валют и акций в формате JSON'''

    utils_logger.info('Старт работы функции get_currency_and_stock')
    currency_and_stock = json.loads('{}')
    file_name = '../user_settings.json'
    try:
        utils_logger.info('Попытка открыть JSON')
        with open(file_name) as f:
            currency_and_stock = json.load(f)
        utils_logger.info('JSON открыт. Возвращаем запрашиваемые данные')
        return currency_and_stock
    except Exception:
        utils_logger.error(f'Что-то пошло не так с {file_name}')
        return currency_and_stock


def get_greeting(user_date_time_str: str) -> str:
    '''Возвращает приветствие в зависимости от времени суток'''

    utils_logger.info('Старт работы функции get_greeting')
    greeting = 'Доброго времени суток'
    try:
        user_date_time = datetime.strptime(user_date_time_str, "%d-%m-%Y %H:%M:%S")
        utils_logger.info('Проверяем, к какому времени суток относится введенное время')
        if 0 <= user_date_time.hour < 6:
            greeting = 'Доброй ночи'
        elif 6 <= user_date_time.hour < 12:
            greeting = 'Доброе утро'
        elif 12 <= user_date_time.hour < 18:
            greeting = 'Добрый день'
        else:
            greeting = 'Добрый вечер'
        utils_logger.info('Возвращаем соответствующее приветствие')
        return greeting
    except Exception:
        utils_logger.error(f'Что-то не так с указанным временем {user_date_time_str}')
        return greeting


def get_card_info(users_data: pd.DataFrame) -> List[dict]:
    '''Возвращает последние 4 цифры карты, общую сумму расходов и кешбэк (1 рубль на каждые 100 рублей)'''

    utils_logger.info('Старт работы функции get_card_info')
    cards_spend_cashback = []
    try:
        utils_logger.info('Преобразуем нужные данные в словарь')
        cards_spend = (
            users_data.loc[users_data["Сумма платежа"] < 0]
            .groupby(by="Номер карты")
            .agg("Сумма платежа")
            .sum()
            .abs()
            .to_dict())
        utils_logger.info('Формируем список нужных данных в заданном формате')
        for card, spend in cards_spend.items():
            cards_spend_cashback.append(
                {'last_digits': card[-4::],
                 'total_spent': round(spend, 2),
                 'cashback': round(spend / 100, 2)})
        utils_logger.info('Возвращаем итоговый список')
        return cards_spend_cashback
    except Exception:
        utils_logger.error('Возникла непредвиденная ошибка')
        return cards_spend_cashback


def get_top_transactions(users_data: pd.DataFrame) -> List[dict]:
    '''Возвращает топ-5 операций по сумме платежа'''

    utils_logger.info('Старт работы функции get_top_transactions')
    top_transactions = []
    try:
        utils_logger.info('Фильтруем пять операций, наибольших по модулю суммы операции')
        user_data_sort = users_data.sort_values('Сумма операции', axis=0, ascending=False, key=lambda x: abs(x)).iloc[
                         0:5]
        users_data_sorted_dict = user_data_sort.to_dict(orient='records')
        utils_logger.info('Добавляем полученные операции в список заданного формата')
        for transaction in users_data_sorted_dict:
            top_transactions.append({'date': str(transaction['Дата платежа']),
                                    'amount': abs(transaction['Сумма операции']),
                                    'category': transaction['Категория'],
                                    'description': transaction['Описание']})
        utils_logger.info('Возвращаем полученный список')
        return top_transactions
    except Exception:
        utils_logger.error('Возникла непредвиденная ошибка')
        return top_transactions


def get_currency_rates(currency_dict: dict) -> List[dict]:
    """Возвращает курс заданных валют"""

    utils_logger.info('Старт работы функции get_currency_rates')
    result_list = []

    currency_list = currency_dict["user_currencies"]
    for currency in currency_list:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        payload: dict = {}
        headers = {"apikey": API_KEY}
        utils_logger.info('Посылаем запрос с указанными параметрами')
        response = requests.request("GET", url, headers=headers, data=payload)
        utils_logger.info('Переводим полученный ответ в JSON формат')
        data = response.json()
        utils_logger.info('Проверяем статус ответа')
        if response.status_code == 200:
            utils_logger.info('Добавляем интересующие нас данные в список в заданном формате')
            result_list.append({"currency": data['query']['from'],
                                    "rate": round(data["result"], 2)})
        else:
            utils_logger.info(f"Запрос не был успешным. Возможная причина: {response.reason}")
            return response.status_code
    utils_logger.info('Выводим полученный список')
    return result_list



def get_stock(stock_dict: dict) -> List[dict]:
    '''Возвращает цены акций заданных компаний'''

    utils_logger.info('Старт работы функции get_stock')
    stock_list = stock_dict['user_stocks']
    stock_prices = []
    utils_logger.info('Проходим по каждой акции в списке stock_dict')
    for stock in stock_list:
        load_dotenv()
        API_KEY_STOCK = os.getenv("API_KEY_STOCK")
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_STOCK}'
        utils_logger.info('Посылаем запрос с указанными параметрами')
        response = requests.request("GET", url)
        data = response.json()
        utils_logger.info('Проверяем статус полученного ответа')
        if response.status_code == 200:
            utils_logger.info('Статус ответа 200. Добавляем интересующие нас данные в список в заданном формате')
            stock_prices.append({'stock': stock,
                                 'price': round(float(data['Global Quote']['05. price']), 2)})
        else:
            utils_logger.info(f"Запрос не был успешным. Возможная причина: {response.reason}")
            return response.reason
    utils_logger.info('Выводим полученный список')
    return stock_prices


# if __name__ == '__main__':
    # print(get_greeting('03-12-2021 06:42:21'))
    # print(get_card_info(get_data_from_date('03-12-2021 06:42:21')))
    # print(get_stock(get_currency_and_stock()))
    # print(get_currency_and_stock())

