import calendar
import json
import logging
from datetime import datetime, timedelta

import pandas as pd

services_logger = logging.getLogger("services")
file_handler = logging.FileHandler("../logs/services.log")
file_formatter = logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
services_logger.addHandler(file_handler)
services_logger.setLevel(logging.INFO)


def get_best_cashback(data: pd.DataFrame, year: int, month: int) -> str:
    """Возвращает выгодные категории повышенного кешбэка"""

    services_logger.info("Старт работы функции get_best_cashback.")
    best_cashback_json: str = '{}'
    try:
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], dayfirst=True)
        start_date = datetime(year, month, 1)
        last_day_month = calendar.monthrange(year, month)
        end_date = datetime(year, month, last_day_month[-1]) + timedelta(days=1)
        services_logger.info("Получаем данные для анализа за выбранный месяц.")
        user_period_data = data[(data["Дата операции"].between(start_date, end_date))]
        services_logger.info("Группируем категории расходов по сумме платежа и переводим данные в словарь.")
        possible_cashback = (
            user_period_data.loc[user_period_data["Сумма платежа"] < 0]
            .groupby(by="Категория")
            .agg("Сумма платежа")
            .sum()
            .abs()
            .to_dict()
        )
        services_logger.info("Сортируем полученный список по убыванию значений.")
        possible_cashback_sort = sorted(possible_cashback.items(), key=lambda item: float(item[1]), reverse=True)
        result_cashback: dict = {}
        services_logger.info("Добавляем три первые пары ключ-значение из полученного списка в итоговый словарь.")
        for category, amount in possible_cashback_sort:
            if len(result_cashback) < 3:
                result_cashback[category] = round(amount / 100, 2)
            else:
                break
        services_logger.info("Переводим полученный итоговый словарь в JSON")
        best_cashback_json_good = json.dumps(result_cashback, indent=4, ensure_ascii=False)
        services_logger.info("Возвращаем полученный JSON. Конец работы функции.")
        return best_cashback_json_good
    except Exception as e:
        services_logger.error(f"Возникла непредвиденная ошибка {e}", exc_info=True)
        return best_cashback_json
