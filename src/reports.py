import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Callable

import pandas as pd

reports_logger = logging.getLogger("reports")
file_handler = logging.FileHandler("../logs/reports.log")
file_formatter = logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
reports_logger.addHandler(file_handler)
reports_logger.setLevel(logging.INFO)


def log(filename: Any = None) -> Callable[[Any], Any]:
    """Записывает в файл результат, который возвращает функция spending_by_category"""

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)

            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                    return result
            else:
                with open("reports.json", "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=4, ensure_ascii=False)
                    return result

        return wrapper

    return decorator


@log()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> str:
    """Возвращает траты по заданной категории за последние три месяца (от переданной даты)"""

    reports_logger.info("Старт работы функции spending_by_category.")
    category_spending: dict = {}
    json_data = json.dumps(category_spending)
    try:
        reports_logger.info("Проверяем, указана ли дата")
        if date is None:
            reports_logger.info("Дата не указана. Берем текущую дату")
            user_date = datetime.now()
        else:
            reports_logger.info("Дата указана пользователем. Берем указанную дату")
            user_date = datetime.strptime(date, "%d-%m-%Y")

        transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], dayfirst=True)
        reports_logger.info("Получаем данные для анализа за три предыдущих месяца от указанной даты.")
        user_period_data = transactions[
            (transactions["Дата операции"].between((user_date - timedelta(days=90)), user_date))
        ]
        reports_logger.info("Фильтруем траты по указанной категории")
        category_spending_df = user_period_data.loc[
            (user_period_data["Сумма платежа"] < 0) & (user_period_data["Категория"] == category)
        ]
        reports_logger.info("Возвращаем дату в текстовое значение.")
        pd.options.mode.chained_assignment = None
        category_spending_df["Дата операции"] = category_spending_df["Дата операции"].dt.strftime("%d-%m-%Y %H:%M:%S")
        reports_logger.info("Переводим DataFrame в словарь.")
        category_spending = category_spending_df.to_dict("index")
        reports_logger.info("Возвращаем полученные траты в JSON  формате.")
        json_data = json.dumps(category_spending, ensure_ascii=False)
        return json_data
    except Exception as e:
        reports_logger.error(f"Возникла непредвиденная ошибка {e}", exc_info=True)
        return json_data
