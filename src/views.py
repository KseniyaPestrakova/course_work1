from datetime import datetime, timedelta
from typing import List
import pandas as pd

user_date_time = datetime.strptime('03-12-2021 06:42:21', "%d-%m-%Y %H:%M:%S")
file_name = '../data/operations.xlsx'
excel_data = pd.read_excel(file_name)
excel_data['Дата операции'] = pd.to_datetime(excel_data['Дата операции'], dayfirst=True)
user_period_data = excel_data[
    (excel_data['Дата операции'].between(user_date_time.replace(day=1), (user_date_time + timedelta(days=1))))]


def get_greeting(user_date_time: datetime) -> str:
    '''Возвращает приветствие в зависимости от времени суток'''
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
    users_data_sorted = users_data.sort_values('Сумма операции', axis=0, ascending=False, key=lambda x: abs(x)).iloc[0:5]
    users_data_sorted_dict = users_data_sorted.to_dict(orient='records')
    top_transactions = []
    for transaction in users_data_sorted_dict:
        top_transactions.append({'date': str(transaction['Дата платежа']),
                                 'amount': abs(transaction['Сумма операции']),
                                 'category': transaction['Категория'],
                                 'description': transaction['Описание']})

    return top_transactions


if __name__ == '__main__':
    print(get_greeting(user_date_time))
    print(get_card_info(user_period_data))
    print(get_top_transactions(user_period_data))
