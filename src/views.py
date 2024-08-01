from datetime import datetime
from typing import List
import pandas as pd

user_date_time = datetime.strptime('03-12-2021 06:42:21', "%d-%m-%Y %H:%M:%S")
file_name = '../data/operations.xlsx'
excel_data = pd.read_excel(file_name)
excel_data['Дата операции'] = pd.to_datetime(excel_data['Дата операции'], dayfirst=True)
user_period_data = excel_data[
    (excel_data['Дата операции'].between(user_date_time.replace(day=1), user_date_time))]


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


def get_card_info() -> List[dict]:
    pass



if __name__ == '__main__':
    print(get_greeting(user_date_time))
