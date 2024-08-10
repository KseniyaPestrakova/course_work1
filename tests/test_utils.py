import json
from unittest.mock import patch, mock_open, Mock

import pandas as pd
import pytest

from src.utils import get_data_frame, get_currency_and_stock, get_greeting, get_card_info, get_top_transactions, \
    get_currency_rates, get_stock


@patch('pandas.read_excel')
def test_get_data_frame_success(mock_read_excel):
    '''Тестируем успешное открытие файла'''
    test_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    mock_read_excel.return_value = test_df

    result = get_data_frame('../data/operations.xlsx')

    assert result.equals(test_df)
    mock_read_excel.assert_called_once_with('../data/operations.xlsx')


def test_get_data_frame_file_not_found():
    '''Тестируем вариант, когда указанный файл не найден'''
    with pytest.raises(FileNotFoundError):
        get_data_frame('../data/wrong.xlsx')


def test_get_currency_and_stock():
    '''Тестируем вывод корректного ответа'''
    mock_data = '{"currencies": ["USD", "EUR"], "stocks": ["AAPL", "MSFT"]}'
    expected_output = {"currencies": ["USD", "EUR"], "stocks": ["AAPL", "MSFT"]}
    with patch('builtins.open', mock_open(read_data=mock_data)):
        result = get_currency_and_stock()

    assert result == expected_output


@pytest.mark.parametrize('user_date_time_str, expected',
                         [("01-12-2021 08:00:00", "Доброе утро"),
                          ("01-12-2021 14:00:00", "Добрый день"),
                          ("01-12-2021 20:00:00", "Добрый вечер"),
                          ("01-12-2021 02:00:00", "Доброй ночи"),
                          ("01-12-2021 25:00:00", "Доброго времени суток")])
def test_get_greeting_morning(user_date_time_str, expected):
    '''Проверяем коррректность вывода приветствия в зависимости от времени суток'''
    assert get_greeting(user_date_time_str) == expected


def test_get_card_info_success():
    '''Проверяем корректный вывод информации по карте'''
    users_data = pd.DataFrame({'Дата операции': ['31.12.2021 16:42:04', '04.12.2021 21:10:00', '01.12.2021 16:26:02'],
                   'Дата платежа': ['31.12.2021', '04.12.2021', '01.12.2021'],
                   'Номер карты': ['*7197', '*7198', '*5091'],
                   'Статус': ['OK', 'OK', 'OK'],
                   'Сумма операции': [-100, -200, -300],
                   'Валюта операции': ['RUB', 'RUB', 'RUB'],
                   'Сумма платежа': [-100, -200, -300],
                   'Валюта платежа': ['RUB', 'RUB', 'RUB'],
                   'Кэшбэк': [None, 1, 55],
                   'Категория': ['Супермаркеты', 'Фастфуд', 'Каршеринг'],
                   'MCC': [5411, 5814, 7512],
                   'Описание': ['Колхоз', 'ЦЕХ 85', 'Ситидрайв'],
                   'Бонусы (включая кэшбэк)': [1, 2, 75],
                   'Округление на инвесткопилку': [0, 0, 0],
                   'Сумма операции с округлением': [100, 200, 300]})
    expected_output = [
        {'last_digits': '5091', 'total_spent': 300.0, 'cashback': 3.0},
        {'last_digits': '7197', 'total_spent': 100.0, 'cashback': 1.0},
        {'last_digits': '7198', 'total_spent': 200.0, 'cashback': 2.0}
    ]
    result = get_card_info(users_data)
    assert result == expected_output

def test_get_card_info_empty_dataframe():
    '''Проверяем отработку неудачной работы функции'''
    users_data = pd.DataFrame({})
    expected_output = []
    result = get_card_info(users_data)
    assert result == expected_output


@pytest.fixture
def sample_data():
    """Пример данных для тестирования."""
    return pd.DataFrame({
        'Дата платежа': ['2021-12-01', '2021-12-02', '2021-12-03', '2021-12-04', '2021-12-05', '2021-12-06'],
        'Сумма операции': [100, -200, 300, -400, 500, -600],
        'Категория': ['Супермаркеты', 'Переводы', 'Каршеринг', 'Дом и ремонт', 'Фастфуд', 'Аптеки'],
        'Описание': ['Колхоз', 'Константин Л.', 'Ситидрайв', 'МаксидоМ', 'Mouse Tail', 'Apteka 23']
    })


def test_get_top_transactions(sample_data):
    """Тестируем получение топ-5 операций."""
    expected_output = [
        {'date': '2021-12-06', 'amount': 600, 'category': 'Аптеки', 'description': 'Apteka 23'},
        {'date': '2021-12-05', 'amount': 500, 'category': 'Фастфуд', 'description': 'Mouse Tail'},
        {'date': '2021-12-04', 'amount': 400, 'category': 'Дом и ремонт', 'description': 'МаксидоМ'},
        {'date': '2021-12-03', 'amount': 300, 'category': 'Каршеринг', 'description': 'Ситидрайв'},
        {'date': '2021-12-02', 'amount': 200, 'category': 'Переводы', 'description': 'Константин Л.'},
    ]

    result = get_top_transactions(sample_data)
    assert result == expected_output


def test_get_top_transactions_empty_dataframe():
    """Тестируем поведение при пустом DataFrame."""
    empty_data = pd.DataFrame(columns=['Дата платежа', 'Сумма операции', 'Категория', 'Описание'])
    result = get_top_transactions(empty_data)
    assert result == []


@pytest.fixture
def currency_data():
    """Пример ответа от API."""
    return {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}


@patch('requests.get')
def test_get_currency_rates_usd(mock_get, currency_data):
    mock_get.return_value.json.return_value = currency_data
    list_currency = [{'currency': 'USD', 'rate': 86.8}]
    assert get_currency_rates(currency_data) == list_currency
#
#
@patch('requests.get')
def test_get_stock(mock_get, currency_data):
    mock_get.return_value.json.return_value = currency_data
    list_currency = [{'price': 216.24, 'stock': 'AAPL'}]
    assert get_stock(currency_data) == list_currency
