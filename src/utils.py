import json
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import requests
from dotenv import load_dotenv
import os


def get_data_from_date(user_date_time_str: str) -> pd.DataFrame:
    '''Возвращает отфильтрованный список транзакций в зависимости от полученной даты'''
    user_date_time = datetime.strptime(user_date_time_str, "%d-%m-%Y %H:%M:%S")

    excel_data = pd.read_excel('../data/operations.xlsx')
    excel_data['Дата операции'] = pd.to_datetime(excel_data['Дата операции'], dayfirst=True)
    user_period_data = excel_data[
        (excel_data['Дата операции'].between(user_date_time.replace(day=1), (user_date_time + timedelta(days=1))))]
    return user_period_data


def get_currency_and_stock() -> json:
    '''Возвращает список валют и акций в формате JSON'''
    with open('../user_settings.json') as f:
        currency_and_stock = json.load(f)
    return currency_and_stock


def get_greeting(user_date_time_str: str) -> str:
    '''Возвращает приветствие в зависимости от времени суток'''
    user_date_time = datetime.strptime(user_date_time_str, "%d-%m-%Y %H:%M:%S")
    if 0 <= user_date_time.hour < 6:
        greeting = 'Доброй ночи'
    elif 6 <= user_date_time.hour < 12:
        greeting = 'Доброе утро'
    elif 12 <= user_date_time.hour < 18:
        greeting = 'Добрый день'
    else:
        greeting = 'Добрый вечер'
    return greeting


def get_card_info(users_data: pd.DataFrame) -> List[dict]:
    '''Возвращает последние 4 цифры карты, общую сумму расходов и кешбэк (1 рубль на каждые 100 рублей)'''
    cards_spend = (
        users_data.loc[users_data["Сумма платежа"] < 0]
        .groupby(by="Номер карты")
        .agg("Сумма платежа")
        .sum()
        .abs()
        .to_dict())
    cards_spend_cashback = []
    for card, spend in cards_spend.items():
        cards_spend_cashback.append(
            {'last_digits': card[-4::],
             'total_spent': round(spend, 2),
             'cashback': round(spend / 100, 2)})

    return cards_spend_cashback


def get_top_transactions(users_data: pd.DataFrame) -> List[dict]:
    '''Возвращает топ-5 операций по сумме платежа'''
    user_data_sort = users_data.sort_values('Сумма операции', axis=0, ascending=False, key=lambda x: abs(x)).iloc[
                        0:5]
    users_data_sorted_dict = user_data_sort.to_dict(orient='records')
    top_transactions = []
    for transaction in users_data_sorted_dict:
        top_transactions.append({'date': str(transaction['Дата платежа']),
                                 'amount': abs(transaction['Сумма операции']),
                                 'category': transaction['Категория'],
                                 'description': transaction['Описание']})

    return top_transactions


def get_currency_rates(currency_dict: dict) -> List[dict]:
    """Возвращает курс заданных валют"""

    result_list = []
    currency_list = currency_dict["user_currencies"]
    for currency in currency_list:
        url = f"https://api.apilayer.com/exchangerates_data/convert?to=RUB&from={currency}&amount=1"
        load_dotenv()
        API_KEY = os.getenv("API_KEY")
        payload: dict = {}
        headers = {"apikey": API_KEY}

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()

        result_list.append({"currency": data['query']['from'],
                            "rate": round(data["result"], 2)})
        if response.status_code == 200:
            continue
        else:
            print(f"Запрос не был успешным. Возможная причина: {response.reason}")
            return response.reason

    return result_list


def get_stock(stock_dict: dict) -> List[dict]:
    '''Возвращает цены акций заданных компаний'''
    stock_list = stock_dict['user_stocks']
    stock_prices = []

    for stock in stock_list:
        load_dotenv()
        API_KEY_STOCK = os.getenv("API_KEY_STOCK")
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_STOCK}'

        response = requests.request("GET", url)
        data = response.json()
        stock_prices.append({'stock': stock,
                             'price': round(float(data['Global Quote']['05. price']), 2)})
        if response.status_code == 200:
            continue
        else:
            print(f"Запрос не был успешным. Возможная причина: {response.reason}")
            return response.reason
    return stock_prices

