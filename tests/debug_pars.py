import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.wildberries_parser import  WildberriesSeleniumParser


def test_final_parser():
    parser = WildberriesSeleniumParser()

    test_url = "https://www.wildberries.ru/catalog/0/search.aspx?search=термопаста"

    try:
        products = parser.parse_search_page(test_url, max_pages=50)

        print(f"\nРезультаты:")
        print(f"Успешно спарсено товаров: {len(products)}")

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_final_parser()