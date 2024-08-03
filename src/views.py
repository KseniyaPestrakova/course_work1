import json
from src.utils import get_data_from_date, get_currency_and_stock, get_greeting, get_card_info, get_top_transactions, \
    get_currency_rates, get_stock


def get_main_page(user_date_time: str) -> json:

    user_data_from_date = get_data_from_date(user_date_time)

    main_page = {"greeting": get_greeting(user_date_time),
                 "cards": get_card_info(user_data_from_date),
                 "top_transactions": get_top_transactions(user_data_from_date),
                 "currency_rates": get_currency_rates(get_currency_and_stock()),
                 "stock_prices": get_stock(get_currency_and_stock())}
    main_page_json = json.dumps(main_page, indent=4, ensure_ascii=False)
    return main_page_json


if __name__ == '__main__':
    print(get_main_page('03-12-2021 06:42:21'))