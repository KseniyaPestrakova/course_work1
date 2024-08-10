from src.reports import spending_by_category
from src.services import get_best_cashback
from src.utils import get_data_frame
from src.views import get_main_page

print(get_main_page("03-12-2021 06:42:21"))
print(get_best_cashback(get_data_frame("../data/operations.xlsx"), 2021, 12))
print(spending_by_category(get_data_frame("../data/operations.xlsx"), "Переводы", "03-12-2021"))
