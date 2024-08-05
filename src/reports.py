import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Any
from utils import get_data_frame
from functools import wraps
import  pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    filename="../logs/reports.log",
    filemode="w",
)

reports_logger = logging.getLogger("reports")


def log(filename: Any = None) -> json:
    """Записывает в файл результат, который возвращает функция spending_by_category"""

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            result_json = result.to_json(orient='records')
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result_json, f, indent=4, ensure_ascii=False)
                    return result
            else:
                with open('reports.json', 'w', encoding="utf-8") as f:
                    json.dump(result_json, f, indent=4, ensure_ascii=False)
                    return result_json
        return wrapper
    return decorator


@log()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    '''Возвращает траты по заданной категории за последние три месяца (от переданной даты)'''

    reports_logger.info('Старт работы функции spending_by_category.')
    category_spending = pd.DataFrame({})
    try:
        reports_logger.info('Проверяем, указана ли дата')
        if date is None:
            reports_logger.info('Дата не указана. Берем текущую дату')
            user_date = datetime.now()
        else:
            reports_logger.info('Дата указана пользователем. Берем указанную дату')
            user_date = datetime.strptime(date, "%d-%m-%Y")

        transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], dayfirst=True)
        reports_logger.info('Получаем данные для анализа за три предыдущих месяца от указанной даты.')
        user_period_data = transactions[(transactions['Дата операции'].between((user_date - timedelta(days=90)), user_date))]
        reports_logger.info('Фильтруем траты по указанной категории')
        category_spending = user_period_data.loc[(user_period_data["Сумма платежа"] < 0) & (user_period_data["Категория"] == category)]
        reports_logger.info('Возвращаем полученные траты.')
        return category_spending
    except Exception:
        reports_logger.error(f'Возникла непредвиденная ошибка {Exception}')
        return category_spending


if __name__ =='__main__':
    print(spending_by_category(get_data_frame('../data/operations.xlsx'), 'Переводы', '03-12-2021'))
