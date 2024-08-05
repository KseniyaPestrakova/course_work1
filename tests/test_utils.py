import json
from unittest.mock import patch

import pandas as pd
import pytest

from src.utils import get_data_frame, get_data_from_date


@pytest.fixture()
def test_df():
    sample_dict = {'Дата операции': ['31.12.2021 16:42:04', '02.12.2021 21:10:00', '01.12.2021 16:26:02'],
                   'Дата платежа': ['31.12.2021', '02.12.2021', '01.12.2021'],
                   'Номер карты': ['*7197', '*7197', '*5091'],
                   'Статус': ['OK', 'OK', 'OK'],
                   'Сумма операции': [-64, -125, -5510,8],
                   'Валюта операции': ['RUB', 'RUB', 'RUB'],
                   'Сумма платежа': [-64, -125, -5510,8],
                   'Валюта платежа': ['RUB', 'RUB', 'RUB'],
                   'Кэшбэк': [None, 1, 55],
                   'Категория': ['Супермаркеты', 'Фастфуд', 'Каршеринг'],
                   'MCC': [5411, 5814, 7512],
                   'Описание': ['Колхоз', 'ЦЕХ 85', 'Ситидрайв'],
                   'Бонусы (включая кэшбэк)': [1, 2, 75],
                   'Округление на инвесткопилку': [0, 0, 0],
                   'Сумма операции с округлением': [64, 125, 5510.80]}
    return pd.DataFrame(sample_dict)


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


@patch('get_data_frame')
def test_get_data_from_date_success(mock_get_data_frame, test_df):
    # Создаем фейковый DataFrame для имитации данных операций

    mock_get_data_frame.return_value = test_df

    user_date_time_str = '31.12.2021 16:42:04'
    result = get_data_from_date(user_date_time_str)

    # Проверяем, что результат содержит только одну транзакцию
    assert len(result) == 1
    assert result['Сумма'].iloc[0] == 200




