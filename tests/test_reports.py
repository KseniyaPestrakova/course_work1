import json
from datetime import datetime

import pytest
import pandas as pd

from src.reports import log, spending_by_category


@pytest.fixture
def sample_transactions():
    # создаем примерные данные для теста
    transactions = pd.DataFrame({
        'Дата операции': ['03-12-2021 09:42:21', '01-12-2021 08:42:21', '25-11-2021 08:42:21', '20-10-2021 12:42:21'],
        'Сумма платежа': [-100.0, -50.0, -200.0, -5000],
        'Категория': ['Супермаркеты', 'Переводы', 'Фастфуд', 'Переводы']
    })
    return transactions


def test_log_decorator(tmp_path, sample_transactions):
    '''Тестируем работу декоратора log'''
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.json"

    @log(filename=str(p))
    def decorated_spending():
        return spending_by_category(sample_transactions, 'Переводы', '03-12-2021')

    decorated_spending()
    assert p.exists()
    with open(p, 'r', encoding="utf-8") as f:
        content = json.load(f)
        assert '01-12-2021' in json.dumps(content)


def test_spending_by_category_with_date(sample_transactions):

    result = spending_by_category(sample_transactions, 'Переводы', '03-12-2021')
    assert '01-12-2021' in result
    assert '20-10-2021' in result
