import json
import pytest
import pandas as pd
import calendar
from src.services import get_best_cashback
from src.utils import get_data_frame


def test_get_best_cashback():
    '''Тестируем успешное выполнение функции get_best_cashback'''
    year = 2021
    month = 12
    result = get_best_cashback(get_data_frame('../data/operations.xlsx'), year, month)
    json_result = json.loads(result)

    assert result is not None
    assert len(json_result) == 3
    assert 'Переводы' in json_result
    assert json_result['ЖКХ'] == 142.16


def test_get_best_cashback_empty_data():
    # создаем примерное значение для теста с пустыми данными
    data = pd.DataFrame({
        'Дата операции': [],
        'Сумма платежа': [],
        'Категория': []
    })

    result = get_best_cashback(data, 2021, 6)
    assert result == '{}'


