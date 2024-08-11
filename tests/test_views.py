import json
from unittest.mock import patch

from src.views import get_main_page



@patch('src.views.get_top_transactions')
@patch('src.views.get_currency_and_stock')
@patch('src.views.get_currency_rates')
@patch('src.views.get_stock')
def test_get_main_page(mock_get_stock, mock_get_currency_rates, mock_get_currency_and_stock,
                       mock_get_top_transactions):
    # Задаем возвращаемые значения для замоканных функций

    mock_get_top_transactions.return_value = [{
            "date": "02.12.2021",
            "amount": 5510.8,
            "category": "Каршеринг",
            "description": "Ситидрайв"
        }]
    mock_get_currency_and_stock.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    mock_get_currency_rates.return_value = [{
            "currency": "USD",
            "rate": 86.8
        }]
    mock_get_stock.return_value = [{
            "stock": "AAPL",
            "price": 216.24
        }]

    user_date_time = '03-12-2021 06:42:21'

    expected_result = {
        "greeting": "Доброе утро",
        "cards": [{
            "last_digits": "5091",
            "total_spent": 9021.2,
            "cashback": 90.21
        },
        {
            "last_digits": "7197",
            "total_spent": 2031.79,
            "cashback": 20.32
        }],
        "top_transactions": [{
            "date": "02.12.2021",
            "amount": 5510.8,
            "category": "Каршеринг",
            "description": "Ситидрайв"
        }],
        "currency_rates": [{
            "currency": "USD",
            "rate": 86.8
        }],
        "stock_prices": [{
            "stock": "AAPL",
            "price": 216.24
        }]
    }

    # Вызываем тестируемую функцию
    result = get_main_page(user_date_time)

    # Преобразуем JSON обратно в словарь для сравнения
    result_dict = json.loads(result)

    # Проверяем, что результат соответствует ожидаемому
    assert result_dict == expected_result

