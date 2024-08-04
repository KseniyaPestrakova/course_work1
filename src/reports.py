import logging
from datetime import datetime, timedelta
from typing import Optional

import  pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(funcName)s - %(levelname)s - %(message)s",
    filename="../logs/reports.log",
    filemode="w",
)

reports_logger = logging.getLogger("reports")


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
        user_period_data = transactions[(transactions['Дата операции'].between((user_date - timedelta(days=91)), user_date))]
        reports_logger.info('Фильтруем траты по указанной категории')
        category_spending = user_period_data.loc[(user_period_data["Сумма платежа"] < 0) & (user_period_data["Категория"] == category)]
        reports_logger.info('Возвращаем полученные траты.')
        return category_spending
    except Exception:
        reports_logger.error(f'Возникла непредвиденная ошибка {Exception}')
        return category_spending


if __name__ =='__main__':
    excel_data = pd.read_excel('../data/operations.xlsx')
    print(spending_by_category(excel_data, 'Переводы', '03-12-2021'))
